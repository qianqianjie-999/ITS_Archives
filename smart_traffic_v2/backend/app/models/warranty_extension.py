from datetime import datetime
from ..extensions import db

class WarrantyExtension(db.Model):
    __tablename__ = 'warranty_extension'

    id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    facility_type: Mapped[str] = db.Column(db.String(50), nullable=False)
    facility_id: Mapped[int] = db.Column(db.Integer, nullable=False)
    project_id: Mapped[int] = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    extension_date: Mapped[datetime] = db.Column(db.Date, nullable=False)

    project: Mapped["Project"] = db.relationship("Project", back_populates="warranty_extensions")

    def to_dict(self):
        return {
            'id': self.id,
            'facility_type': self.facility_type,
            'facility_id': self.facility_id,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'extension_date': self.extension_date.isoformat() if self.extension_date else None
        }