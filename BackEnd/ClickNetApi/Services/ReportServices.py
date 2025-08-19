import io
import base64
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from pathlib import Path
from Schemas.shared import SystemLogErrorSchema
from Services.LogServices import AddLogOrError
import traceback

report_template_path = Path(__file__).resolve().parent.parent / "Templates"

async def GenerateStatement(transactions: list,
                        account_no: str,
                        account_holder: str,
                        opening_balance: float,
                        current_balance: float,
                        currency: str
                    ) -> str:
    try:
        total_dr = 0.0
        total_cr = 0.0
        rendered_transactions = []

        for tx in transactions:
            dr = tx.amount if tx.dr_cr.upper() == "D" else 0.0
            cr = tx.amount if tx.dr_cr.upper() == "C" else 0.0
            total_dr += dr
            total_cr += cr

            rendered_transactions.append({
                "trans_date": tx.trans_date.strftime("%d-%b-%Y %H:%M"),
                "narration": tx.narration,
                "dr_amount": f"{dr:.2f}" if dr > 0 else "",
                "cr_amount": f"{cr:.2f}" if cr > 0 else "",
                "currency": tx.currency_nm.upper() if tx.currency_nm else "N/A",
                "trans_id": tx.trans_id
            })

        # Load HTML template
        env = Environment(
            loader=FileSystemLoader(report_template_path),
            autoescape=select_autoescape(["html", "xml"])
        )
        template = env.get_template("statement_template.html")

        html_content = template.render(
            account_no=account_no,
            account_holder=account_holder,
            opening_balance=f"{opening_balance:.2f}",
            current_balance=f"{current_balance:.2f}",
            currency=currency.upper(),
            transactions=rendered_transactions,
            total_dr=f"{total_dr:.2f}",
            total_cr=f"{total_cr:.2f}",
            generated_on=datetime.now().strftime("%d-%b-%Y %H:%M")
        )

        # Convert HTML to PDF
        html = HTML(string=html_content, base_url=str(report_template_path.resolve()))
        buffer = io.BytesIO()
        html.write_pdf(target=buffer)
        buffer.seek(0)

        # Convert PDF to Base64
        return base64.b64encode(buffer.read()).decode("utf-8")

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="ReportServices/_GenerateStatement",
            CreatedBy=""
        ))
        raise Exception(ex)