from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:12345@localhost:3306/SHOPPINGAI"
)