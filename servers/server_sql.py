from mcp.server.fastmcp import FastMCP
import psycopg2, json

mcp = FastMCP("SQL", dependencies=["psycopg2"])

SERVER = "143.244.215.137"
PORT = "5432"
DATABASE = "novadrive"
USERNAME = "etlreadonly"
PASSWORD = "novadrive376A@"

CONN_STR = {
    "host": SERVER,
    "port": PORT,
    "dbname": DATABASE,
    "user": USERNAME,
    "password": PASSWORD,
}

def get_connection():
    return psycopg2.connect(**CONN_STR)

@mcp.tool()
def get_schema():
    """Retorna tabelas e colunas do schema padrão"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
        
        schema = {}
        for table_name, column_name, data_type in cursor.fetchall():
            if table_name not in schema:
                schema[table_name] = []
            schema[table_name].append({"column": column_name, "type": data_type})

        cursor.close()
        conn.close()
        
        return json.dumps({"schema": schema}, indent=4, sort_keys=True, default=str)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def health_check() -> bool:
    """Indica se a conexão esta funcional com o banco de dados"""
    try:
        conn = get_connection()
        conn.close()
        return True
    except:
        return False

@mcp.tool()
def query(sql: str) -> str:
    """Executa uma consulta no banco de dados"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
        cursor.close()
        conn.close()
        return json.dumps(result, indent=4, sort_keys=True, default=str)
    except Exception as e:
        return str(e)
    
