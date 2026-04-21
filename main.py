from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session


from database import get_db


# fastapi 객체 생성
app = FastAPI()
# jinja2 템플릿 객체 생성 (templates 파일들이 어디에 있는지 알려야 한다.)
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        # 응답에 필요한 data 를 context 로 전달 할수 있다.
        context={
            "fortuneToday":"동쪽으로 가면 귀인을 만나요"
        }
    )


# get 방식 /post 요청 처리
@app.get("/post", response_class=HTMLResponse)
def getPosts(request: Request, db:Session = Depends(get_db)):
    # DB 에서 글목록을 가져오기 위한 sql 문 준비
    query = text("""
        SELECT num, writer, title, content, created_at
        FROM post
        ORDER BY num DESC
    """)
    # 글 목록을 얻어와서
    result = db.execute(query)
    posts = result.fetchall()
    # 응답하기
    return templates.TemplateResponse(
        request=request,
        name="post/list.html", # templates/post/list.html jinja2 를 해석한 결과를 응답
        context={
            "posts":posts
        }
    )

@app.get("/post/new", response_class=HTMLResponse)
def postNew(request: Request):
    return templates.TemplateResponse(request=request, name="post/new-form.html")

@app.post("/post/new")
def postNew(writer: str = Form(...), title: str = Form(...), content: str = Form(...),
            db: Session = Depends(get_db)):
    query = text("""
        INSERT INTO post
        (writer, title, content)
        VALUES(:writer, :title, :content)
    """)  
    db.execute(query, {"writer":writer, "title":title, "content":content})
    db.commit()
    
    return RedirectResponse("/post", status_code=302)         
    
@app.post("/post/delete/{num}")
def delete_post(num: int, db: Session = Depends(get_db)):
    # 1. Prepare the SQL command
    query = text("DELETE FROM post WHERE num = :num")
    
    # 2. Execute with the specific ID
    db.execute(query, {"num": num})
    
    # 3. Commit to save changes
    db.commit()
    
    # 4. Redirect back to the list page
    return RedirectResponse(url="/post", status_code=303)

# 1. Show the Edit Page
@app.get("/post/post-edits/{num}", response_class=HTMLResponse)
def edit_form(num: int, request: Request, db: Session = Depends(get_db)):
    # Find the specific post
    query = text("SELECT num, title, content FROM post WHERE num = :num")
    post = db.execute(query, {"num": num}).mappings().first()
    
    return templates.TemplateResponse(
    request=request, 
    name="post/post-edits.html", 
    context={"post": post}
    )


# 2. Handle the Update
@app.post("/post/update/{num}")
def update_post(
    num: int, 
    writer: str = Form(...),
    title: str = Form(...), 
    content: str = Form(...), 
    db: Session = Depends(get_db)
):
    query = text("""
        UPDATE post 
        SET writer = :writer, title = :title, content = :content 
        WHERE num = :num
    """)
    db.execute(query, {"writer": writer, "title": title, "content": content, "num": num})
    db.commit()
    
    return RedirectResponse(url="/post", status_code=303)