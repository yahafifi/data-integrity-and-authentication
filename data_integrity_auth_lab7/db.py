import pyodbc
from config import Config

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{SQL Server}};"
        f"SERVER={Config.SERVER};"
        f"DATABASE={Config.DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return conn