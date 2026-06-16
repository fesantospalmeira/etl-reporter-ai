import os
import sys
import smtplib
from datetime import datetime
from email.message import EmailMessage
from loguru import logger
import google.generativeai as genai

class LoggerSender:
    def __init__(
        self,
        pipeline_name:str,
        log_file: str,
        to_list: list,
        subject: str,
        email_user: str = None,
        email_password: str = None,
        gemini_api_key: str = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 465
    ):
        self.pipeline = pipeline_name
        self.log_file = log_file
        self.to_list = to_list 
        self.subject = subject
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        self.email_user = email_user or os.getenv("EMAIL_USER")
        self.email_password = email_password or os.getenv("EMAIL_PASSWORD")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        if not self.email_user or not self.email_password:
            logger.warning("Credenciais de e-mail não encontradas. O envio poderá falhar.")

        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.ai_model = genai.GenerativeModel('gemini-flash-latest')
        else:
            self.ai_model = None
            logger.warning("Variável GEMINI_API_KEY não encontrada. A análise de IA será desativada.")
  
    def _get_ai_insights(self) -> str:
            """Extrai as linhas de erro do log e pede para a IA resumir o problema."""
            if not os.path.exists(self.log_file):
                return "Log não encontrado para análise da IA."

            linhas_de_erro = []
            with open(self.log_file, "r", encoding="utf-8") as f:
                for linha in f:
                    if "| ERROR" in linha or "❌" in linha:
                        linhas_de_erro.append(linha.strip())

            if not linhas_de_erro:
                return "Nenhum erro crítico detectado pela IA."

            erros_para_analisar = "\n".join(linhas_de_erro[-15:])
            
            prompt = f"""
            Você é um Engenheiro de Dados Sênior. Analise os seguintes logs de erro de um processo de ETL com o nome de {self.pipeline}:
            {erros_para_analisar}
            
            Por favor, forneça:
            1. Um resumo curto e direto de qual foi o problema principal.
            2. Uma sugestão prática de como corrigir.
            Seja breve, no máximo 2 parágrafos.
            3.Não dê nenhuma identificação sobre você, como por exemplo dizer: "Como Engenheiro de Dados Sênior.."
            """
            
            try:
                resposta = self.ai_model.generate_content(prompt)
                return resposta.text
            except Exception as e:
                return f"Falha ao gerar análise da IA: {e}"
               
    def setup_logger(self):
        """Configura o Loguru para exportar os logs para o arquivo definido e para o console."""
        logger.remove()
        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{module}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
        logger.add(self.log_file, rotation="10 MB", retention="30 days", level="INFO")
        
    def _count_errors_and_warnings(self) -> tuple[int, int]:
        """Conta quantos erros e warnings existem no log atual."""
        erros = 0
        warnings = 0
        
        if not os.path.exists(self.log_file):
            logger.warning(f"O arquivo de log {self.log_file} não existe para contagem.")
            return 0, 0

        with open(self.log_file, "r", encoding="utf-8") as f:
            for linha in f:
                if "| ERROR" in linha or "❌" in linha:
                    erros += 1
                elif "| WARNING" in linha or "⚠️" in linha:
                    warnings += 1

        return erros, warnings

    def send_log_to_email(self):
        """Envia o log por e-mail com template dinâmico baseado em erros e avisos."""
        if not os.path.exists(self.log_file):
            logger.error(f"Não foi possível enviar o e-mail: O arquivo {self.log_file} não existe.")
            return

        if not self.email_user or not self.email_password:
            logger.error("Credenciais de e-mail não configuradas.")
            return

        erros, warnings = self._count_errors_and_warnings()
        data_atual = datetime.now().strftime("%d/%m/%Y às %H:%M")

        if erros > 0:
            cor_status = "#d9534f" 
            texto_status = "Falha / Com Erros"
        elif warnings > 0:
            cor_status = "#f0ad4e"
            texto_status = "Atenção / Avisos"
        else:
            cor_status = "#5cb85c"
            texto_status = "Sucesso Total"
            #Envio o email de sucesso apenas para mim
            self.to_list = ['felipesantos7938@gmail.com']

        dynamic_subject = f"[{texto_status}] {self.subject} - Erros: {erros} | Warnings: {warnings}"
        
        insight_ia_html = ""
        if erros > 0:
            analise_ia = self._get_ai_insights()
            insight_ia_html = f"""
            <div style="background-color: #e8f4fd; border-left: 4px solid #1a73e8; padding: 15px; margin-top: 20px;">
                <h3 style="margin-top: 0; color: #1a73e8; font-size: 16px;">🤖 Análise da IA (Diagnóstico)</h3>
                <p style="font-size: 14px; margin-bottom: 0;">{analise_ia.replace(chr(10), '<br>')}</p>
            </div>
            """

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            
            <div style="background-color: {cor_status}; color: white; padding: 20px; text-align: center;">
                <h2 style="margin: 0; font-size: 22px;">📊 Relatório de Execução do ETL</h2>
                <p style="margin: 5px 0 0 0; font-size: 14px;">Pipeline: {self.pipeline} </p>
            </div>
            
            <div style="padding: 30px;">
                <p style="font-size: 16px;">A rotina de sincronização de dados foi finalizada. Abaixo está o resumo da operação e uma análise via inteligência artificial:</p>
            <div style="padding: 30px;">
                {insight_ia_html}           
            </div>
                <table style="width: 100%; border-collapse: collapse; margin-top: 25px; font-size: 15px;">
                <tr>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee;"><strong>Data da Finalização:</strong></td>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: right;">{data_atual}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee;"><strong>Status Final:</strong></td>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: right;"><strong><span style="color: {cor_status};">{texto_status}</span></strong></td>
                </tr>
                <tr>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee;"><strong>Erros Críticos:</strong></td>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: right; color: #d9534f;"><strong>{erros}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee;"><strong>Avisos (Warnings):</strong></td>
                    <td style="padding: 12px 0; border-bottom: 1px solid #eee; text-align: right; color: #f0ad4e;"><strong>{warnings}</strong></td>
                </tr>
                </table>
                
                <p style="margin-top: 30px; font-size: 14px; color: #555;">
                O arquivo de log completo (<strong>{os.path.basename(self.log_file)}</strong>) está anexado a este e-mail para auditoria e debug detalhado.
                </p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee;">
                <p style="margin: 0;">Este é um e-mail automático. Porém pode ser respondido.</p>
            </div>
            
            </div>
        </body>
        </html>
        """

        msg = EmailMessage()
        msg["From"] = self.email_user
        msg["To"] = ", ".join(self.to_list) 
        msg["Subject"] = dynamic_subject
        
        msg.set_content("Seu cliente de e-mail não suporta a visualização em HTML. O log está em anexo.")
        msg.add_alternative(html_content, subtype='html')

        with open(self.log_file, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(self.log_file)
            msg.add_attachment(file_data, maintype="text", subtype="plain", filename=file_name)

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
                smtp.login(self.email_user, self.email_password)
                smtp.send_message(msg)

            logger.success(f"E-mail de log enviado com sucesso para: {', '.join(self.to_list)}")

        except Exception as e:
            logger.error(f"Falha crítica ao enviar o log por e-mail: {e}")