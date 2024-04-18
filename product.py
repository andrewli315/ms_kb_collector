from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

Base = declarative_base()


def create_local_engine():
    global Base
    engine = create_engine('sqlite:///hotfix.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine, autoflush=False)
    session = Session()
    return session

Product_KB_Relation = Table(
    'Prod_KB',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('Product.id')),
    Column('patch_id', Integer, ForeignKey('Patch.id'))) 


class Product(Base):
    __tablename__ = "Product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    productID = Column(String)
    name = Column(String)
    kb_numbers = relationship('KB_Number', secondary=Product_KB_Relation, back_populates='affected_products')
    def __init__(self, _id, _name):
        self.productID = _id
        self.name = _name
        self.kb_num = []
    def add_kb_num(self, kb):
        self.kb_numbers.append(kb)
    def __repr__(self):
        kbs = []
        for i in self.kb_numbers:
            kbs.append(i)

        return '{}->{}: {}'.format(self.productID, self.name, kbs)

class KB_Number(Base):
    
    __tablename__ = "Patch"
    id = Column(Integer, primary_key=True, autoincrement=True)
    patch_number = Column(String)
    date = Column(DateTime)
    affected_products = relationship('Product', secondary=Product_KB_Relation, back_populates='kb_numbers')
    def __init__(self, _patch_num, _date):
        self.patch_number = _patch_num
        self.date = _date
    def add_affected_product(self, products):
        self.affected_products = products
    
    def __repr__(self):
        return "{}".format(self.patch_number)

'''

if __name__ == "__main__":
    kb="KB5034127"
    date = "2024-01-09T08:00:00"
    affected_items = {}
    affected_items['11568'] = "Windows 10 Version 1809 for 32-bit Systems"
    affected_items['11569'] = "Windows 10 Version 1809 for x64-based Systems"
    affected_items['11570'] = "Windows 10 Version 1809 for ARM64-based Systems"
    affected_items['11571'] = "Windows Server 2019"
    affected_items['11572'] = "Windows Server 2019 (Server Core installation)"


    session = create_local_engine()
    products = [] 
    kb_instance = KB_Number(kb, datetime.fromisoformat(date))
    for item in affected_items:
        print("{} {}".format(item, affected_items[item]))
        tmp = Product(item, affected_items[item])
        tmp.add_kb_num(kb_instance)
        products.append(tmp)
    session.add_all(products)

    kb_instance.add_affected_product(products)
    session.add(kb_instance)
    session.commit()

    kb = session.query(KB_Number).all()[0]
    for affected_product in kb.affected_products:
        print(affected_product)

'''


    
