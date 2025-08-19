import subprocess
import json
import os
from typing import List, Dict, Any

class Courses:
    def __init__(self, working_dir: str = "cartridge_current_working_state"):
        self.working_dir = working_dir
        self.python_bin = ".venv/bin/python"
        self.cli_script = "cartridge_cli.py"
    
    def _run_command(self, args: List[str]) -> tuple[str, str, bool]:
        """Run cartridge CLI command and return (stdout, stderr, success)"""
        cmd = [self.python_bin, self.cli_script] + args
        print(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            stdout = result.stdout.strip()
            print(f"Command succeeded: {stdout}")
            return stdout, "", True
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.strip()
            print(f"Command failed: {' '.join(cmd)}")
            print(f"Error: {stderr}")
            return "", stderr, False
    
    def _get_cartridge_path(self, course_name: str) -> str:
        """Get full path to cartridge directory"""
        return os.path.join(self.working_dir, course_name)
    
    @property
    def courses(self) -> List[List]:
        """Get courses in the old format for compatibility"""
        course_list = []
        
        if not os.path.exists(self.working_dir):
            return []
        
        for course_name in os.listdir(self.working_dir):
            course_path = self._get_cartridge_path(course_name)
            if os.path.isdir(course_path):
                # Get course data
                output, error, success = self._run_command(["list", course_path, "--json"])
                if success and output:
                    try:
                        course_data = json.loads(output)
                        modules = []
                        for module in course_data.get("modules", []):
                            module_dict = {
                                "title": module["title"],
                                "items": []
                            }
                            for item in module.get("items", []):
                                module_dict["items"].append({
                                    "title": item["title"],
                                    "content_type": item["content_type"],
                                    "content": "placeholder content"
                                })
                            modules.append(module_dict)
                        course_list.append([course_name, modules])
                    except json.JSONDecodeError:
                        course_list.append([course_name, []])
        
        return course_list
    
    @property
    def course_names(self) -> List[str]:
        """Get course names from directories"""
        if not os.path.exists(self.working_dir):
            return []
        
        return [name for name in os.listdir(self.working_dir) 
                if os.path.isdir(os.path.join(self.working_dir, name))]
    
    def add_course(self, course_name: str, title: str = None, code: str = None):
        """Create a new cartridge"""
        course_path = self._get_cartridge_path(course_name)
        if os.path.exists(course_path):
            return  # Course already exists
        
        # Create cartridge with CLI
        args = ["create", course_path]
        if title:
            args.extend(["--title", title.strip()])
        else:
            args.extend(["--title", course_name.strip()])
        if code:
            args.extend(["--code", code.strip()])
        else:
            args.extend(["--code", course_name.strip().upper()])
        
        output, error, success = self._run_command(args)
        return success, output if success else error
    
    def update_course_name(self, old_name: str, new_name: str):
        """Rename a course directory"""
        old_path = self._get_cartridge_path(old_name)
        new_path = self._get_cartridge_path(new_name)
        
        if os.path.exists(old_path) and not os.path.exists(new_path):
            os.rename(old_path, new_path)
    
    def delete_course(self, course_name: str):
        """Delete a course and its cartridge"""
        course_path = self._get_cartridge_path(course_name)
        if os.path.exists(course_path):
            import shutil
            shutil.rmtree(course_path)
    
    def add_module(self, course_name: str, module_name: str):
        """Add a module to a cartridge"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        # Get current modules to determine position
        modules = self.get_course_modules(course_name)
        position = len(modules) + 1
        
        output, error, success = self._run_command([
            "add-module", course_path, 
            "--title", module_name.strip(), 
            "--position", str(position)
        ])
        return success, output if success else error
    
    def update_module(self, course_name: str, current_title: str, new_title: str, position: int = None):
        """Update a module using the cartridge CLI"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        # Build command arguments
        args = [
            "update-module", course_path,
            "--title", current_title.strip(),
            "--new-title", new_title.strip()
        ]
        
        # Add position if provided
        if position is not None:
            args.extend(["--position", str(position)])
        
        output, error, success = self._run_command(args)
        return success, output if success else error
    
    def delete_module(self, course_name: str, module_name: str):
        """Delete a module using the cartridge CLI"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        output, error, success = self._run_command([
            "delete-module", course_path,
            "--title", module_name.strip()
        ])
        return success, output if success else error
    
    def get_course_modules(self, course_name: str) -> List[dict]:
        """Get all modules for a specific course"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return []
        
        output, error, success = self._run_command(["list", course_path, "--json"])
        if success and output:
            try:
                course_data = json.loads(output)
                return course_data.get("modules", [])
            except json.JSONDecodeError:
                return []
        return []
    
    def get_module_items(self, course_name: str, module_name: str) -> List[dict]:
        """Get all items for a specific module"""
        modules = self.get_course_modules(course_name)
        for module in modules:
            if module.get("title") == module_name:
                return module.get("items", [])
        return []
    
    def add_module_item(self, course_name: str, module_name: str, item_title: str, content_type: str, **kwargs):
        """Add an item to a specific module"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        if content_type == "WikiPage":
            output, error, success = self._run_command([
                "add-wiki", course_path,
                "--module", module_name.strip(),
                "--title", item_title.strip(),
                "--content", kwargs.get("content", "placeholder content").strip()
            ])
            return success, output if success else error
            
        elif content_type == "Assignment":
            output, error, success = self._run_command([
                "add-assignment", course_path,
                "--module", module_name.strip(),
                "--title", item_title.strip(),
                "--content", kwargs.get("content", "Assignment description").strip(),
                "--points", str(kwargs.get("points", 10))
            ])
            return success, output if success else error
            
        elif content_type == "DiscussionTopic":
            output, error, success = self._run_command([
                "add-discussion", course_path,
                "--module", module_name.strip(),
                "--title", item_title.strip(),
                "--description", kwargs.get("description", "Discussion topic description").strip()
            ])
            return success, output if success else error
            
        elif content_type == "File":
            output, error, success = self._run_command([
                "add-file", course_path,
                "--module", module_name.strip(),
                "--filename", item_title.strip(),
                "--content", kwargs.get("content", "File content here").strip()
            ])
            return success, output if success else error
            
        elif content_type == "Quiz":
            output, error, success = self._run_command([
                "add-quiz", course_path,
                "--module", module_name.strip(),
                "--title", item_title.strip(),
                "--description", kwargs.get("description", "Quiz description").strip(),
                "--points", str(kwargs.get("points", 10))
            ])
            return success, output if success else error
            
        return False, f"Unsupported content type: {content_type}"
    
    def delete_module_item(self, course_name: str, module_name: str, item_title: str, content_type: str):
        """Delete an item from a specific module"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        if content_type == "WikiPage":
            output, error, success = self._run_command([
                "delete-wiki", course_path,
                "--title", item_title.strip()
            ])
            return success, output if success else error
            
        elif content_type == "Assignment":
            output, error, success = self._run_command([
                "delete-assignment", course_path,
                "--title", item_title.strip()
            ])
            return success, output if success else error
            
        elif content_type == "DiscussionTopic":
            output, error, success = self._run_command([
                "delete-discussion", course_path,
                "--title", item_title.strip()
            ])
            return success, output if success else error
            
        elif content_type == "File":
            output, error, success = self._run_command([
                "delete-file", course_path,
                "--filename", item_title.strip()
            ])
            return success, output if success else error
            
        elif content_type == "Quiz":
            output, error, success = self._run_command([
                "delete-quiz", course_path,
                "--title", item_title.strip()
            ])
            return success, output if success else error
            
        return False, f"Unsupported content type: {content_type}"
    
    def update_module_item(self, course_name: str, module_name: str, old_item_title: str, content_type: str, **kwargs):
        """Update an item in a specific module"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        if content_type == "WikiPage":
            args = ["update-wiki", course_path, "--title", old_item_title.strip()]
            if kwargs.get("new_title"):
                args.extend(["--new-title", kwargs["new_title"].strip()])
            if kwargs.get("content"):
                args.extend(["--content", kwargs["content"].strip()])
            if kwargs.get("position") is not None:
                args.extend(["--position", str(kwargs["position"])])
                
        elif content_type == "Assignment":
            args = ["update-assignment", course_path, "--title", old_item_title.strip()]
            if kwargs.get("new_title"):
                args.extend(["--new-title", kwargs["new_title"].strip()])
            if kwargs.get("content"):
                args.extend(["--content", kwargs["content"].strip()])
            if kwargs.get("points") is not None:
                args.extend(["--points", str(int(kwargs["points"]))])
            if kwargs.get("position") is not None:
                args.extend(["--position", str(kwargs["position"])])
                
        elif content_type == "DiscussionTopic":
            args = ["update-discussion", course_path, "--title", old_item_title.strip()]
            if kwargs.get("new_title"):
                args.extend(["--new-title", kwargs["new_title"].strip()])
            if kwargs.get("content"):
                args.extend(["--content", kwargs["content"].strip()])
            if kwargs.get("position") is not None:
                args.extend(["--position", str(kwargs["position"])])
                
        elif content_type == "Quiz":
            args = ["update-quiz", course_path, "--title", old_item_title.strip()]
            if kwargs.get("new_title"):
                args.extend(["--new-title", kwargs["new_title"].strip()])
            if kwargs.get("description"):
                args.extend(["--description", kwargs["description"].strip()])
            if kwargs.get("points") is not None:
                args.extend(["--points", str(kwargs["points"])])
            if kwargs.get("position") is not None:
                args.extend(["--position", str(kwargs["position"])])
                
        elif content_type == "File":
            args = ["update-file", course_path, "--filename", old_item_title.strip()]
            if kwargs.get("new_filename"):
                args.extend(["--new-filename", kwargs["new_filename"].strip()])
            if kwargs.get("content"):
                args.extend(["--content", kwargs["content"].strip()])
            if kwargs.get("position") is not None:
                args.extend(["--position", str(kwargs["position"])])
        else:
            return False, f"Unsupported content type: {content_type}"
        
        output, error, success = self._run_command(args)
        return success, output if success else error
    
    def get_item_details(self, course_name: str, module_name: str, item_title: str, content_type: str = None) -> Dict[str, Any]:
        """Get detailed information about a specific item"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return {}
        
        # If no content_type provided, try to find it from module items
        if not content_type:
            module_items = self.get_module_items(course_name, module_name)
            for item in module_items:
                if item.get("title") == item_title:
                    content_type = item.get("content_type")
                    break
        
        if not content_type:
            return {}
        
        # Map content types to CLI commands
        command_map = {
            "WikiPage": ["display-wiki", "--title", item_title.strip()],
            "Assignment": ["display-assignment", "--title", item_title.strip()],
            "DiscussionTopic": ["display-discussion", "--title", item_title.strip()],
            "Quiz": ["display-quiz", "--title", item_title.strip()],
            "File": ["display-file", "--filename", item_title.strip()]
        }
        
        command_args = command_map.get(content_type)
        if not command_args:
            return {}
        
        output, error, success = self._run_command([command_args[0], course_path] + command_args[1:])
        
        if success and output:
            try:
                data = json.loads(output)
                # Ensure content_type is included in the response
                data["content_type"] = content_type
                return data
            except json.JSONDecodeError:
                return {}
        return {}
    
    def copy_item(self, course_name: str, item_title: str, target_module: str, content_type: str):
        """Copy an item to a different module"""
        course_path = self._get_cartridge_path(course_name)
        if not os.path.exists(course_path):
            return False, f"Course '{course_name}' not found"
        
        if content_type == "WikiPage":
            output, error, success = self._run_command([
                "copy-wiki", course_path,
                "--title", item_title.strip(),
                "--target-module", target_module.strip()
            ])
            return success, output if success else error
            
        elif content_type == "Assignment":
            output, error, success = self._run_command([
                "copy-assignment", course_path,
                "--title", item_title.strip(),
                "--target-module", target_module.strip()
            ])
            return success, output if success else error
            
        elif content_type == "DiscussionTopic":
            output, error, success = self._run_command([
                "copy-discussion", course_path,
                "--title", item_title.strip(),
                "--target-module", target_module.strip()
            ])
            return success, output if success else error
            
        elif content_type == "File":
            output, error, success = self._run_command([
                "copy-file", course_path,
                "--filename", item_title.strip(),
                "--target-module", target_module.strip()
            ])
            return success, output if success else error
            
        elif content_type == "Quiz":
            output, error, success = self._run_command([
                "copy-quiz", course_path,
                "--title", item_title.strip(),
                "--target-module", target_module.strip()
            ])
            return success, output if success else error
            
        return False, f"Unsupported content type: {content_type}"