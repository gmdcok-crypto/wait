"""Notification adapters: Kakao Alimtalk first, SMS fallback.

Real Kakao/SMS vendor APIs differ by partner. Keep interfaces stable and
swap HTTP calls inside implementations when credentials are ready.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from app.config import Settings, get_settings
from app.models.call_log import NotifyChannel

logger = logging.getLogger(__name__)


@dataclass
class NotifyResult:
    success: bool
    channel: NotifyChannel
    message: str
    provider_ref: Optional[str] = None


class Notifier(ABC):
    @abstractmethod
    def send_waiting(self, phone: str, store_name: str, number: int) -> NotifyResult:
        raise NotImplementedError

    @abstractmethod
    def send_call(
        self, phone: str, store_name: str, number: int, recall: bool = False
    ) -> NotifyResult:
        raise NotImplementedError


class ConsoleNotifier(Notifier):
    """Local/dev notifier — logs instead of sending."""

    def send_waiting(self, phone: str, store_name: str, number: int) -> NotifyResult:
        msg = "[{0}] 대기번호 {1}번이 등록되었습니다.".format(store_name, number)
        logger.info("[NOTIFY waiting] to=%s msg=%s", phone, msg)
        print("[CONSOLE NOTIFY] waiting -> {0}: {1}".format(phone, msg))
        return NotifyResult(True, NotifyChannel.console, msg, provider_ref="console")

    def send_call(
        self, phone: str, store_name: str, number: int, recall: bool = False
    ) -> NotifyResult:
        prefix = "재호출" if recall else "호출"
        msg = "[{0}] {1}번 고객님, 지금 입장해 주세요. ({2})".format(
            store_name, number, prefix
        )
        logger.info("[NOTIFY call] to=%s msg=%s", phone, msg)
        print("[CONSOLE NOTIFY] call -> {0}: {1}".format(phone, msg))
        return NotifyResult(True, NotifyChannel.console, msg, provider_ref="console")


class KakaoSmsNotifier(Notifier):
    """Kakao Alimtalk with SMS fallback."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def send_waiting(self, phone: str, store_name: str, number: int) -> NotifyResult:
        msg = "[{0}] 대기번호 {1}번이 등록되었습니다.".format(store_name, number)
        return self._send(
            phone=phone,
            message=msg,
            template_code=self.settings.kakao_template_waiting,
            variables={"store": store_name, "number": str(number)},
        )

    def send_call(
        self, phone: str, store_name: str, number: int, recall: bool = False
    ) -> NotifyResult:
        prefix = "재호출" if recall else "호출"
        msg = "[{0}] {1}번 고객님, 지금 입장해 주세요. ({2})".format(
            store_name, number, prefix
        )
        return self._send(
            phone=phone,
            message=msg,
            template_code=self.settings.kakao_template_call,
            variables={"store": store_name, "number": str(number)},
        )

    def _send(
        self,
        phone: str,
        message: str,
        template_code: str,
        variables: Dict[str, str],
    ) -> NotifyResult:
        kakao = self._try_kakao(phone, template_code, variables, message)
        if kakao.success:
            return kakao

        sms = self._try_sms(phone, message)
        if sms.success:
            return sms

        logger.warning("Kakao and SMS failed for %s; falling back to console log", phone)
        print("[FALLBACK CONSOLE] -> {0}: {1}".format(phone, message))
        return NotifyResult(True, NotifyChannel.console, message, provider_ref="fallback-console")

    def _try_kakao(
        self,
        phone: str,
        template_code: str,
        variables: Dict[str, str],
        message: str,
    ) -> NotifyResult:
        if not self.settings.kakao_api_key or not self.settings.kakao_sender_key:
            return NotifyResult(False, NotifyChannel.kakao, "kakao credentials missing")

        payload = {
            "senderKey": self.settings.kakao_sender_key,
            "templateCode": template_code,
            "recipient": phone,
            "variables": variables,
            "message": message,
        }
        headers = {"Authorization": "Bearer {0}".format(self.settings.kakao_api_key)}
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    "https://example-kakao-partner.invalid/v1/alimtalk/send",
                    json=payload,
                    headers=headers,
                )
            if resp.status_code < 300:
                ref = None
                try:
                    ref = resp.json().get("messageId")
                except Exception:
                    ref = None
                return NotifyResult(True, NotifyChannel.kakao, message, provider_ref=ref)
            logger.error("Kakao send failed: %s %s", resp.status_code, resp.text)
            return NotifyResult(False, NotifyChannel.kakao, "kakao http {0}".format(resp.status_code))
        except Exception as exc:
            logger.exception("Kakao send error")
            return NotifyResult(False, NotifyChannel.kakao, str(exc))

    def _try_sms(self, phone: str, message: str) -> NotifyResult:
        if not self.settings.sms_api_key:
            return NotifyResult(False, NotifyChannel.sms, "sms credentials missing")

        payload = {
            "to": phone,
            "from": self.settings.sms_from,
            "text": message,
        }
        headers = {
            "Authorization": "Bearer {0}".format(self.settings.sms_api_key),
        }
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    "https://example-sms-partner.invalid/v1/sms/send",
                    json=payload,
                    headers=headers,
                )
            if resp.status_code < 300:
                return NotifyResult(True, NotifyChannel.sms, message, provider_ref="sms")
            logger.error("SMS send failed: %s %s", resp.status_code, resp.text)
            return NotifyResult(False, NotifyChannel.sms, "sms http {0}".format(resp.status_code))
        except Exception as exc:
            logger.exception("SMS send error")
            return NotifyResult(False, NotifyChannel.sms, str(exc))


def get_notifier(settings: Optional[Settings] = None) -> Notifier:
    settings = settings or get_settings()
    if settings.notify_mode == "kakao_sms":
        return KakaoSmsNotifier(settings)
    return ConsoleNotifier()
