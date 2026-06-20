"""
Email Service — SMTP Only
──────────────────────────
Sends emails via SMTP (e.g. Gmail, Outlook, Azure SMTP relay).
Works reliably from Azure deployments and all hosting platforms.

Setup:
  Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM in .env
  
  For Gmail:  SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, use App Password
  For Outlook: SMTP_HOST=smtp.office365.com, SMTP_PORT=587
  For Azure Communication Services: SMTP_HOST=smtp.azurecomm.net, SMTP_PORT=587
"""

import ssl
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


# ── SMTP Send ─────────────────────────────────────────

async def _send_via_smtp(to_email: str, subject: str, html_body: str, plain_text: str):
    """Send email via SMTP with robust TLS handling for Azure and other hosts."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print(f"⚠️ SMTP not configured. Skipping email to {to_email}")
        print(f"   Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM in .env")
        return

    message = MIMEMultipart("alternative")
    message["From"] = settings.EMAIL_FROM or settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_body, "html"))

    smtp_kwargs = {
        "hostname": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "username": settings.SMTP_USER,
        "password": settings.SMTP_PASSWORD,
        "timeout": 30,
    }

    # Port 465 uses implicit SSL; port 587 (and others) use STARTTLS
    if settings.SMTP_PORT == 465:
        smtp_kwargs["use_tls"] = True
    else:
        smtp_kwargs["start_tls"] = True

    try:
        await aiosmtplib.send(message, **smtp_kwargs)
        print(f"✅ Email sent to {to_email} (via SMTP)")
    except aiosmtplib.SMTPConnectError as e:
        print(f"❌ SMTP connection failed: {e}")
        # Retry with relaxed TLS (some Azure/cloud hosts need this)
        try:
            tls_context = ssl.create_default_context()
            tls_context.check_hostname = False
            tls_context.verify_mode = ssl.CERT_NONE
            smtp_kwargs["tls_context"] = tls_context
            await aiosmtplib.send(message, **smtp_kwargs)
            print(f"✅ Email sent to {to_email} (via SMTP with relaxed TLS)")
        except Exception as retry_err:
            print(f"❌ SMTP retry also failed: {retry_err}")
            raise
    except Exception as e:
        print(f"❌ SMTP error for {to_email}: {e}")
        raise


# ── Unified Send ─────────────────────────────────────

async def _send_email(to_email: str, subject: str, html_body: str, plain_text: str):
    """Send an email using SMTP."""
    await _send_via_smtp(to_email, subject, html_body, plain_text)


# ── Public API ────────────────────────────────────────

async def send_interview_invitations(candidates: list, session: dict, company_name: str):
    """Send invitation emails to all candidates for an interview session."""
    for candidate in candidates:
        try:
            await _send_single_invite(
                to_email=candidate.email,
                unique_token=candidate.unique_token,
                session=session,
                company_name=company_name,
            )
        except Exception as e:
            print(f"Failed to send email to {candidate.email}: {e}")


async def _send_single_invite(to_email: str, unique_token: str, session: dict, company_name: str):
    """Send a single invitation email."""
    base_url = settings.PUBLIC_URL or settings.FRONTEND_URL
    interview_link = f"{base_url}/interview/{unique_token}"
    scheduled = session.get("scheduled_time")
    date_str = scheduled.strftime("%B %d, %Y") if scheduled else "TBD"
    time_str = scheduled.strftime("%I:%M %p") if scheduled else "TBD"
    # Strip leading zero from hour (e.g. "02:30 PM" -> "2:30 PM")
    if time_str.startswith("0"):
        time_str = time_str[1:]
    job_role = session.get("job_role", "Position")

    subject = f"Interview Invitation – {company_name}"

    html_body = f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8fafc;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; border-radius: 16px 16px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">Interview Invitation</h1>
            <p style="color: #e0d4f5; margin-top: 8px; font-size: 16px;">{company_name}</p>
        </div>
        <div style="background: #ffffff; padding: 36px 30px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 16px 16px;">
            <p style="color: #334155; font-size: 16px; line-height: 1.6;">Dear Candidate,</p>
            <p style="color: #334155; font-size: 16px; line-height: 1.6;">
                You are invited to attend an AI-powered interview for the <strong style="color: #1e293b;">{job_role}</strong> position.
            </p>

            <div style="background: #f1f5f9; padding: 24px; border-radius: 12px; margin: 24px 0; border-left: 4px solid #667eea;">
                <p style="margin: 6px 0; color: #475569; font-size: 15px;"><strong>📅 Date:</strong> {date_str}</p>
                <p style="margin: 6px 0; color: #475569; font-size: 15px;"><strong>🕐 Time:</strong> {time_str}</p>
                <p style="margin: 6px 0; color: #475569; font-size: 15px;"><strong>⏱️ Duration:</strong> {session.get('duration_minutes', 30)} minutes</p>
            </div>

            <p style="color: #334155; font-size: 16px; line-height: 1.6;">Please join the interview using the link below at the scheduled time:</p>

            <div style="text-align: center; margin: 30px 0;">
                <a href="{interview_link}"
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 16px 36px; text-decoration: none;
                          border-radius: 12px; font-size: 16px; font-weight: 600;
                          display: inline-block; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
                    Join Interview →
                </a>
            </div>

            <p style="color: #94a3b8; font-size: 13px; line-height: 1.5;">
                If the button doesn't work, copy this link:<br/>
                <a href="{interview_link}" style="color: #667eea; word-break: break-all;">{interview_link}</a>
            </p>

            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;"/>

            <div style="background: #eff6ff; border-radius: 8px; padding: 16px; margin-top: 8px;">
                <p style="color: #1e40af; font-size: 13px; margin: 0; font-weight: 600;">💡 Tips for your interview:</p>
                <ul style="color: #3b82f6; font-size: 13px; margin: 8px 0 0; padding-left: 20px; line-height: 1.8;">
                    <li>Ensure a stable internet connection</li>
                    <li>Use a quiet room with good lighting</li>
                    <li>Have your camera and microphone ready</li>
                    <li>This is an AI-powered interview — answer clearly and concisely</li>
                </ul>
            </div>

            <p style="color: #94a3b8; font-size: 12px; margin-top: 20px;">
                This is a unique link generated for you. Please do not share it.
            </p>
        </div>
    </body>
    </html>
    """

    plain_text = f"""Dear Candidate,

You are invited to attend the interview for the {job_role} position at {company_name}.

Date: {date_str}
Time: {time_str}
Duration: {session.get('duration_minutes', 30)} minutes

Join Link: {interview_link}

Tips:
- Ensure a stable internet connection
- Use a quiet room with good lighting
- Have your camera and microphone ready
- This is an AI-powered interview — answer clearly and concisely

Best regards,
{company_name}
"""

    await _send_email(to_email, subject, html_body, plain_text)
