from sqlalchemy.orm import Session

import models.transaction as models


def get_transactions(db: Session):
    return db.query(models.Transaction).all()
