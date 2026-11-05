from app.core.config import settings


def send_otp(email: str, code: str) -> None:
    if settings.OTP_DELIVERY_MODE == "console":
        print(f"[SkySense OTP] email={email} code={code} ttl={settings.OTP_TTL_SECONDS}s")
        return
    if settings.OTP_DELIVERY_MODE == "ses":
        import boto3
        ses = boto3.client("ses", region_name=settings.AWS_REGION)
        ses.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": "Código de verificación SkySense"},
                "Body": {"Text": {"Data": f"Tu código OTP es {code}. Expira en {settings.OTP_TTL_SECONDS // 60} minutos."}},
            },
        )
        return
    raise RuntimeError(f"Unsupported OTP_DELIVERY_MODE={settings.OTP_DELIVERY_MODE}")
