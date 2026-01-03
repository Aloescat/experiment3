# app/main.py

import sys
import os

# 修复：将当前目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：创建数据库表
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")
    yield
    # 关闭时：可以添加清理代码
    print("Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title="Student Management API",
    description="API for managing students and groups",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
from app.endpoints import students, groups
app.include_router(students.router)
app.include_router(groups.router)


@app.get("/")
def read_root():
    return {
        "message": "Student Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}