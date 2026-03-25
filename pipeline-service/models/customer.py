from sqlalchemy import Column, String, Date, DECIMAL, TIMESTAMP, func
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id        = Column(String(50), primary_key=True)
    first_name         = Column(String(100), nullable=False)
    last_name          = Column(String(100), nullable=False)
    email              = Column(String(255), nullable=False)
    phone              = Column(String(20))
    address            = Column(String)
    date_of_birth      = Column(Date)
    account_balance    = Column(DECIMAL(15, 2))
    platform_created_at = Column(TIMESTAMP)

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
        return {
            "customer_id":        self.customer_id,
            "first_name":         self.first_name,
            "last_name":          self.last_name,
            "email":              self.email,
            "phone":              self.phone,
            "address":            self.address,
            "date_of_birth":      str(self.date_of_birth) if self.date_of_birth else None,
            "account_balance":    float(self.account_balance) if self.account_balance else None,
            "platform_created_at": str(self.platform_created_at) if self.platform_created_at else None,
            "created_at":         str(self.created_at) if self.created_at else None,
            "updated_at":         str(self.updated_at) if self.updated_at else None,
        }