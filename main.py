from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import shutil, os

from database import engine, get_db
from models import Base, User, Role, UserRole, Document
from schemas import UserCreate, RoleCreate
from auth import create_token, require_roles, get_user_role
from pdf_utils import extract_text_from_pdf
from rag import create_index, rag_search, delete_index, search_all_documents

Base.metadata.create_all(bind=engine)

app =  FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# AUTH

@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(username = user.username, password = user.password)
    db.add(new_user)
    db.commit()
    return {"msg":"User Created"}

@app.post("/auth/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    token = create_token({"user_id": db_user.id})
    return {"access_token": token}

# ROLES

@app.post("/roles/create")
def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    db.add(Role(name=role.name))
    db.commit()
    return {"msg":"Role Created"}

@app.post("/users/assign-role")
def assign_role(user_id: int, role_id: int, db: Session = Depends(get_db)):
    db.add(UserRole(user_id = user_id, role_id = role_id))
    db.commit()
    return {"msg": "Role Assigned"}

# USERS

@app.get("/users/{user_id}/roles")
def get_user_roles_api(
    user_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin"]))
):
    roles = (
        db.query(Role.name).join(UserRole, Role.id == UserRole.role_id).filter(UserRole.user_id == user_id).all()
    )

    return {"roles": [r[0] for r in roles]}

@app.get("/users/{user_id}/permissions")
def get_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin"]))
):
    roles = (
        db.query(Role.name).join(UserRole, Role.id == UserRole.role_id).filter(UserRole.user_id == user_id).all()
    )

    role_names = [r[0] for r in roles]

    permissions = []

    if "Admin" in role_names:
        permissions.append("Full Access")
    
    if "Financial Analyst" in role_names:
        permissions.append("Upload/Edit")
    
    if "Auditor" in role_names:
        permissions.append("Review")

    if "Client" in role_names:
        permissions.append("View")

    return {"roles": role_names, "permissions": permissions}

# DOCUMENTS

@app.post("/documents/upload")
def upload_doc(
    file: UploadFile = File(...),
    title: str = "",
    company_name: str = "",
    document_type: str = "",
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin", "Financial Analyst"]))
):
    path = f"{UPLOAD_DIR}/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = Document(
        title = title,
        company_name = company_name,
        document_type = document_type,
        file_path = path,
        uploaded_by = user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"msg": "Uploaded", "doc_id": doc.id}

@app.get("/documents")
def get_docs(
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin", "Client", "Auditor","Financial Analyst"]))
    ):
    return db.query(Document).all()

@app.get("/documents/search")
def search_documents(
    company_name: str = None,
    document_type: str = None,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin", "Client", "Auditor", "Financial Analyst"]))
):
    query = db.query(Document)

    if company_name:
        query = query.filter(Document.company_name == company_name)

    if document_type:
        query = query.filter(Document.document_type == document_type)

    return query.all()

@app.get("/documents/{doc_id}")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin", "Client", "Auditor", "Financial Analyst"]))
):
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document Not Found")

    return doc

@app.delete("/documents/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles(["Admin", "Financial Analyst"]))
):
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document Not Found")
    
    if doc.uploaded_by != user.id:
        user_roles = [r for r in get_user_role(user.id, db)]
        if "Admin" not in user_roles:
            raise HTTPException(status_code=403, detail="Not Allowed")
        
    db.delete(doc)
    db.commit()

    return {"msg": "Document Deleted"}

# RAG

@app.post("/rag/index-document")
def index_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(404)
    
    text = extract_text_from_pdf(doc.file_path)
    create_index(doc_id, text)

    return {"msg": "Indexed"}

@app.post("/rag/search")
def search(query: str):
    return {"answer": search_all_documents(query)}

@app.delete("/rag/remove-document/{doc_id}")
def remove_document_embeddings(doc_id: int):
    if delete_index(doc_id):
        return {"msg": "Deleted Embedding"}
    return {"msg":"No Embedding Found"}

@app.get("/rag/context/{doc_id}")
def get_context(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404)
    
    text = extract_text_from_pdf(doc.file_path)

    return {"context": text[:1000]}