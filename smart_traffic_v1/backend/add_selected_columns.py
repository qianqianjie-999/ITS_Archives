from app.extensions import db
from app import create_app
import sqlalchemy

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        # 添加路口表的信号灯选中字段
        result = conn.execute(sqlalchemy.text("DESCRIBE intersection"))
        columns = [row[0] for row in result.fetchall()]
        if 'selected_traffic_light_id' not in columns:
            conn.execute(sqlalchemy.text('ALTER TABLE intersection ADD COLUMN selected_traffic_light_id INTEGER NULL'))
            print("Added column: selected_traffic_light_id to intersection")
        
        # 添加路口表的电子警察选中字段
        if 'selected_electronic_police_id' not in columns:
            conn.execute(sqlalchemy.text('ALTER TABLE intersection ADD COLUMN selected_electronic_police_id INTEGER NULL'))
            print("Added column: selected_electronic_police_id to intersection")
        
        # 添加违停点位表的选中字段
        result = conn.execute(sqlalchemy.text("DESCRIBE parking_enforcement_point"))
        columns = [row[0] for row in result.fetchall()]
        if 'selected_project_id' not in columns:
            conn.execute(sqlalchemy.text('ALTER TABLE parking_enforcement_point ADD COLUMN selected_project_id INTEGER NULL'))
            print("Added column: selected_project_id to parking_enforcement_point")
        
        # 添加卡口点位表的选中字段
        result = conn.execute(sqlalchemy.text("DESCRIBE checkpoint_point"))
        columns = [row[0] for row in result.fetchall()]
        if 'selected_project_id' not in columns:
            conn.execute(sqlalchemy.text('ALTER TABLE checkpoint_point ADD COLUMN selected_project_id INTEGER NULL'))
            print("Added column: selected_project_id to checkpoint_point")
        
        # 添加结构化点位表的选中字段
        result = conn.execute(sqlalchemy.text("DESCRIBE sky_net_point"))
        columns = [row[0] for row in result.fetchall()]
        if 'selected_project_id' not in columns:
            conn.execute(sqlalchemy.text('ALTER TABLE sky_net_point ADD COLUMN selected_project_id INTEGER NULL'))
            print("Added column: selected_project_id to sky_net_point")
        
        conn.commit()
        print("Done!")