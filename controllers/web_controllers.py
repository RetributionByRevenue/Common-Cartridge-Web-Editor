from fastapi import APIRouter, WebSocket, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
from .asyncqueue import AsyncQueue
from .auth import require_login, verify_credentials
from models.user_state import UserState
from models.courses import Courses
import asyncio

router = APIRouter()
templates = Jinja2Templates(directory="views")
message_queue = AsyncQueue()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # If already logged in, redirect to home
    if request.session.get("username"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login/login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_credentials(username, password):
        request.session["username"] = username
        return RedirectResponse(url="/", status_code=303)
    else:
        return templates.TemplateResponse("login/login.html", {"request": request, "error": "Invalid username or password"})

@router.post("/logout")
async def logout(request: Request):
    # Check if user is logged in
    username = request.session.get("username")
    if username:    
        request.session.clear()
        await message_queue.broadcast_js_to_user("window.location='login'" , username)
        return None

@router.post("/submit")
async def submit_form(request: Request):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    await message_queue.broadcast_js_to_user('''   $.LoadingOverlay("show");   ''', username)
    await asyncio.sleep(3)
    await message_queue.broadcast_js_to_user('''  $.LoadingOverlay("hide", true); ''', username)
    return RedirectResponse(url="/", status_code=303)

@router.post("/add-course")
async def add_course(request: Request, course_name: str = Form(...)):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Add course using CLI
    courses = Courses()
    success, message = courses.add_course(course_name)
    
    if success:
        # Render the accordion macro to get HTML content
        macro_template = templates.get_template("index/course_pagination_component.html")
        html_content = macro_template.module.course_accordion(courses.courses)
        
        # Update DOM with new course list
        jquery_update = f'$("div.demo-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        # Hide loading overlay and show success
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Hide loading overlay and show error
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    #close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.post("/edit/{course_name}")
async def edit_course(request: Request, course_name: str, new_course_name: str = Form(alias="course_name")):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Update course name in shelve
    courses = Courses()
    courses.update_course_name(course_name, new_course_name)
    
    # Render the accordion macro to get updated HTML content
    macro_template = templates.get_template("index/course_pagination_component.html")
    html_content = macro_template.module.course_accordion(courses.courses)
    
    # Update DOM with new course list
    jquery_update = f'$("div.demo-container").html(`{html_content}`);'
    await message_queue.broadcast_js_to_user(jquery_update, username)
    
    # Hide loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
    await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.post("/delete/{course_name}")
async def delete_course(request: Request, course_name: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Delete course from shelve
    courses = Courses()
    courses.delete_course(course_name)
    
    # Render the accordion macro to get updated HTML content
    macro_template = templates.get_template("index/course_pagination_component.html")
    html_content = macro_template.module.course_accordion(courses.courses)
    
    # Update DOM with new course list
    jquery_update = f'$("div.demo-container").html(`{html_content}`);'
    await message_queue.broadcast_js_to_user(jquery_update, username)
    
    # Hide loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
    await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.post("/add-module/{course_name}")
async def add_module(request: Request, course_name: str, module_name: str = Form(...)):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Add module to course using CLI
    courses = Courses()
    success, message = courses.add_module(course_name, module_name)
    
    if success:
        # Render the accordion macro to get updated HTML content
        macro_template = templates.get_template("index/course_pagination_component.html")
        html_content = macro_template.module.course_accordion(courses.courses)
        
        # Update DOM with new course list
        jquery_update = f'$("div.demo-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        # Hide loading overlay and show success
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Hide loading overlay and show error
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.post("/update-module/{course_name}/{module_title}")
async def update_module(request: Request, course_name: str, module_title: str, 
                       new_title: str = Form(...), position: int = Form(None)):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Update module using CLI
    courses = Courses()
    success, message = courses.update_module(course_name, module_title, new_title, position)
    
    if success:
        # Render the accordion macro to get updated HTML content
        macro_template = templates.get_template("index/course_pagination_component.html")
        html_content = macro_template.module.course_accordion(courses.courses)
        
        # Update DOM with new course list
        jquery_update = f'$("div.demo-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        # Hide loading overlay and show success
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Hide loading overlay and show error
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.post("/edit-module/{course_name}/{module_name}")
async def edit_module(request: Request, course_name: str, module_name: str, new_module_name: str = Form(alias="module_name")):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Update module name in shelve
    courses = Courses()
    courses.update_module_name(course_name, module_name, new_module_name)
    
    # Render the accordion macro to get updated HTML content
    macro_template = templates.get_template("index/course_pagination_component.html")
    html_content = macro_template.module.course_accordion(courses.courses)
    
    # Update DOM with new course list
    jquery_update = f'$("div.demo-container").html(`{html_content}`);'
    await message_queue.broadcast_js_to_user(jquery_update, username)
    
    # Hide loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
    await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.post("/delete-module/{course_name}/{module_name}")
async def delete_module(request: Request, course_name: str, module_name: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Delete module from course
    courses = Courses()
    success, message = courses.delete_module(course_name, module_name)
    
    # Hide loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
    
    if success:
        # Render the accordion macro to get updated HTML content
        macro_template = templates.get_template("index/course_pagination_component.html")
        html_content = macro_template.module.course_accordion(courses.courses)
        
        # Update DOM with new course list
        jquery_update = f'$("div.demo-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Show error message
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url="/", status_code=303)

@router.get("/view_module/{course_name}/{module_name}", response_class=HTMLResponse)
async def view_module(request: Request, course_name: str, module_name: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Create user state for request
    user_state = UserState(username)
    
    # Get courses from shelve to verify module exists
    courses = Courses()
    modules = courses.get_course_modules(course_name)
    

    module_names_arr = []
    for i in range(0,len(modules)):
        module_names_arr.append(modules[i].get("title"))

    # Check if module exists
    module_exists = any(module.get("title") == module_name for module in modules)
    
    if not module_exists:
        return RedirectResponse(url="/", status_code=303)
    
    # Get module items
    module_items = courses.get_module_items(course_name, module_name)
    
    return templates.TemplateResponse("view_module/view_module.html", {
        "request": request,
        "message": user_state.message,
        "username": username,
        "course_name": course_name,
        "module_name": module_name,
        "module_items": module_items,
        "module_name_arr": module_names_arr
    })

@router.post("/add-item/{course_name}/{module_name}")
async def add_item(request: Request, course_name: str, module_name: str, item_title: str = Form(...), content_type: str = Form(...)):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Add item to module using CLI with default values for additional parameters
    courses = Courses()
    success, message = courses.add_module_item(
        course_name, 
        module_name, 
        item_title, 
        content_type,
        content="Default content",
        description="Default description", 
        points=10
    )
    
    if success:
        # Get updated module items
        module_items = courses.get_module_items(course_name, module_name)
        
        # Get module names array for the macro
        modules = courses.get_course_modules(course_name)
        module_names_arr = [module.get("title") for module in modules] if modules else []
        
        # Render the module items macro to get updated HTML content
        macro_template = templates.get_template("view_module/module_items_component.html")
        html_content = macro_template.module.module_items_display(module_items, course_name, module_name, module_names_arr)
        
        # Update DOM with new module items
        jquery_update = f'$("div.module-items-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        # Hide loading overlay and show success
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Hide loading overlay and show error
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url=f"/view_module/{course_name}/{module_name}", status_code=303)

@router.post("/delete-item/{course_name}/{module_name}/{item_title}/{content_type}")
async def delete_item(request: Request, course_name: str, module_name: str, item_title: str, content_type: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Delete item from module using CLI
    courses = Courses()
    success, message = courses.delete_module_item(course_name, module_name, item_title, content_type)
    
    if success:
        # Get updated module items
        module_items = courses.get_module_items(course_name, module_name)
        
        # Get module names array for the macro
        modules = courses.get_course_modules(course_name)
        module_names_arr = [module.get("title") for module in modules] if modules else []
        
        # Render the module items macro to get updated HTML content
        macro_template = templates.get_template("view_module/module_items_component.html")
        html_content = macro_template.module.module_items_display(module_items, course_name, module_name, module_names_arr)
        
        # Update DOM with new module items
        jquery_update = f'$("div.module-items-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        # Hide loading overlay and show success
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Hide loading overlay and show error
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url=f"/view_module/{course_name}/{module_name}", status_code=303)

@router.post("/copy-item/{course_name}/{module_name}/{item_title}/{content_type}")
async def copy_item(request: Request, course_name: str, module_name: str, item_title: str, content_type: str, destination_module: str = Form(...)):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Copy item using CLI
    courses = Courses()
    success, message = courses.copy_item(course_name, item_title, destination_module, content_type)
    
    if success:
        # Get updated module items
        module_items = courses.get_module_items(course_name, module_name)
        
        # Get module names array for the macro
        modules = courses.get_course_modules(course_name)
        module_names_arr = [module.get("title") for module in modules] if modules else []
        
        # Render the module items macro to get updated HTML content
        macro_template = templates.get_template("view_module/module_items_component.html")
        html_content = macro_template.module.module_items_display(module_items, course_name, module_name, module_names_arr)
        
        # Update DOM with new module items
        jquery_update = f'$("div.module-items-container").html(`{html_content}`);'
        await message_queue.broadcast_js_to_user(jquery_update, username)
        
        # Hide loading overlay and show success
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        # Hide loading overlay and show error
        await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    # Close modal
    await message_queue.broadcast_js_to_user(''' $('.jquery-modal.blocker.current').remove(); ''', username)

    return RedirectResponse(url=f"/view_module/{course_name}/{module_name}", status_code=303)

@router.get("/view-item/{course_name}/{module_name}/{item_title}/{content_type}", response_class=HTMLResponse)
async def view_item(request: Request, course_name: str, module_name: str, item_title: str, content_type: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Create user state for request
    user_state = UserState(username)
    
    # Get item details from CLI
    courses = Courses()
    item = courses.get_item_details(course_name, module_name, item_title, content_type)
    print("dubug!!!!!!!!!!!!!!!!!!!!")
    print(item)
    
    if not item:
        return RedirectResponse(url=f"/view_module/{course_name}/{module_name}", status_code=303)
    
    # Select template based on content type
    template_map = {
        "WikiPage": "view-item/view-WikiPage.html",
        "Assignment": "view-item/view-Assignment.html", 
        "DiscussionTopic": "view-item/view-DiscussionTopic.html",
        "File": "view-item/view-File.html",
        "Quiz": "view-item/view-Quiz.html"
    }
    
    template_name = template_map.get(content_type, "view-item/view-item.html")
    
    return templates.TemplateResponse(template_name, {
        "request": request,
        "message": user_state.message,
        "username": username,
        "course_name": course_name,
        "module_name": module_name,
        "item": item,
        "content_type": content_type
    })

@router.post("/update-item/{course_name}/{module_name}/{item_title}/{content_type}")
async def update_item(request: Request, course_name: str, module_name: str, item_title: str, content_type: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Show loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("show");', username)
    
    # Get form data
    form_data = await request.form()
    
    # Build update parameters based on content type
    kwargs = {}
    
    # Common fields
    if "item_title" in form_data:
        kwargs["new_title"] = form_data["item_title"]
    if "position" in form_data and form_data["position"]:
        kwargs["position"] = int(form_data["position"])
    
    # Content type specific fields
    if content_type == "WikiPage":
        if "content" in form_data:
            kwargs["content"] = form_data["content"]
            
    elif content_type == "Assignment":
        if "content" in form_data:
            kwargs["content"] = form_data["content"]
        if "points" in form_data and form_data["points"]:
            kwargs["points"] = float(form_data["points"])
            
    elif content_type == "DiscussionTopic":
        if "content" in form_data:
            kwargs["content"] = form_data["content"]
            
    elif content_type == "Quiz":
        if "description" in form_data:
            kwargs["description"] = form_data["description"]
        if "points" in form_data and form_data["points"]:
            kwargs["points"] = float(form_data["points"])
            
    elif content_type == "File":
        if "new_filename" in form_data:
            kwargs["new_filename"] = form_data["new_filename"]
        if "content" in form_data:
            kwargs["content"] = form_data["content"]
    
    # Update item using CLI
    courses = Courses()
    success, message = courses.update_module_item(course_name, module_name, item_title, content_type, **kwargs)
    
    # Hide loading overlay
    await message_queue.broadcast_js_to_user('$.LoadingOverlay("hide", true);', username)
    
    if success:
        await message_queue.broadcast_js_to_user('''alertify.success("Success");''', username)
    else:
        await message_queue.broadcast_js_to_user('''alertify.error("Error, please check logs");''', username)

    return None


@router.websocket("/live/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    await message_queue.add_websocket(websocket, username)
    
    # Initialize user state
    user_state = UserState(username)
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            event = payload.get("event")
            
            if event == "run-js":
                await message_queue.broadcast_js_to_user("console.log('server connection established')", username)
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await message_queue.remove_websocket(websocket, username)



@router.get("/download/{course_name}")
async def download_course(request: Request, course_name: str):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    import os
    import base64
    import subprocess
    from fastapi.responses import FileResponse
    
    # Define the course directory path
    course_dir = os.path.join("cartridge_current_working_state", course_name)
    
    if not os.path.exists(course_dir):
        print(f"Course directory not found: {course_dir}")
        return {"message": "Course directory not found", "course_name": course_name}
    
    changed_files = []
    
    # Recursively walk through all directories and files
    for root, dirs, files in os.walk(course_dir):
        for file in files:
            # Skip table_inspect.html
            if file == "table_inspect.html":
                print(f"Skipping file: {file}")
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file contains base64 markers
                if "@@@@@@@@@@" in content:
                    # Count occurrences to ensure we have at least 2 markers
                    marker_count = content.count("@@@@@@@@@@")
                    if marker_count >= 2:
                        # Split content by markers
                        parts = content.split("@@@@@@@@@@")
                        
                        if len(parts) >= 3:
                            # Get the base64 content (middle part)
                            base64_content = parts[1]
                            
                            try:
                                # Decode base64
                                decoded_content = base64.b64decode(base64_content).decode('utf-8')
                                
                                # Replace the content: keep everything before first marker,
                                # add decoded content, keep everything after last marker
                                new_content = parts[0] + decoded_content + parts[2]
                                
                                # Write back to file
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(new_content)
                                
                                changed_files.append(file_path)
                                print(f"Changed file: {file_path}")
                                
                            except Exception as e:
                                print(f"Error decoding base64 in {file_path}: {e}")
                                
            except Exception as e:
                # Skip files that can't be read as text (binary files, etc.)
                continue
    
    print(f"Total files changed: {len(changed_files)}")
    for file_path in changed_files:
        print(f"File changed: {file_path}")
    
    # Run CLI commands
    try:
        # Run list command
        list_cmd = [".venv/bin/python", "cartridge_cli.py", "list", course_dir]
        print(f"Running command: {' '.join(list_cmd)}")
        list_result = subprocess.run(list_cmd, capture_output=True, text=True, check=True)
        print(f"List command output: {list_result.stdout}")
        
        # Run package command
        package_cmd = [".venv/bin/python", "cartridge_cli.py", "package", course_dir]
        print(f"Running command: {' '.join(package_cmd)}")
        package_result = subprocess.run(package_cmd, capture_output=True, text=True, check=True)
        print(f"Package command output: {package_result.stdout}")
        
        # Look for the generated zip file (assuming it's created in the course directory or parent)
        zip_filename = f"{course_name}.zip"
        zip_path = os.path.join(course_dir, zip_filename)
        
        # If not found in course dir, check parent directory
        if not os.path.exists(zip_path):
            zip_path = os.path.join("cartridge_current_working_state", zip_filename)
        
        # If still not found, check current directory
        if not os.path.exists(zip_path):
            zip_path = zip_filename
        
        if os.path.exists(zip_path):
            print(f"Serving download file: {zip_path}")
            return FileResponse(
                path=zip_path,
                filename=zip_filename,
                media_type='application/zip'
            )
        else:
            print(f"Generated zip file not found: {zip_filename}")
            return {"message": "Package created but zip file not found", "course_name": course_name}
            
    except subprocess.CalledProcessError as e:
        print(f"CLI command failed: {e}")
        print(f"Error output: {e.stderr}")
        return {"message": "CLI command failed", "course_name": course_name, "error": str(e)}


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    # Check if user is logged in
    username = request.session.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    # Create user state for request
    user_state = UserState(username)
    
    # Get courses from shelve
    courses = Courses()
    
    return templates.TemplateResponse("index/index.html", {
        "request": request, 
        "message": user_state.message,
        "username": username,
        "courses": courses.course_names,
        "courses_data": courses.courses
    })


