import shutil
from pathlib import Path


class CartridgeDeletionMixin:
    """
    Mixin class containing deletion methods for CartridgeGenerator.
    This mixin provides methods to delete various cartridge components by their identifiers.
    """

    def delete_wiki_page_by_id(self, page_id):
        """Delete a wiki page by its identifier (page ID or resource ID)"""
        # Find the wiki page in our internal list
        page_to_delete = None
        for i, page in enumerate(self.wiki_pages):
            if page['identifier'] == page_id or page['resource_id'] == page_id:
                page_to_delete = page
                page_index = i
                break
        
        if not page_to_delete:
            raise ValueError(f"Wiki page with identifier {page_id} not found")
        
        resource_id = page_to_delete['resource_id']
        
        # Remove from wiki_pages list
        self.wiki_pages.pop(page_index)
        
        # Remove from resources list
        self.resources = [r for r in self.resources if r['identifier'] != resource_id]
        
        # Remove from modules and organization items
        for module in self.modules:
            # Find and remove the module item that references this wiki page
            items_to_remove = []
            for item in module['items']:
                if item['identifierref'] == resource_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove from organization structure
        for org_module in self.organization_items:
            items_to_remove = []
            for item in org_module['items']:
                if item['identifierref'] == resource_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                org_module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in org_module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove the physical wiki page file if it exists
        if self.output_dir:
            wiki_file_path = Path(self.output_dir) / page_to_delete['filename']
            if wiki_file_path.exists():
                wiki_file_path.unlink()
                print(f"Removed wiki file: {page_to_delete['filename']}")
        
        # Update cartridge state
        self._update_cartridge_state()
        
        print(f"Wiki page '{page_to_delete['title']}' (ID: {page_id}) has been deleted")
        return True

    def delete_assignment_by_id(self, assignment_id):
        """Delete an assignment by its identifier"""
        # Find the assignment in our internal list
        assignment_to_delete = None
        for i, assignment in enumerate(self.assignments):
            if assignment['identifier'] == assignment_id:
                assignment_to_delete = assignment
                assignment_index = i
                break
        
        if not assignment_to_delete:
            raise ValueError(f"Assignment with identifier {assignment_id} not found")
        
        # Remove from assignments list
        self.assignments.pop(assignment_index)
        
        # Remove from resources list
        self.resources = [r for r in self.resources if r['identifier'] != assignment_id]
        
        # Remove from modules and organization items
        for module in self.modules:
            # Find and remove the module item that references this assignment
            items_to_remove = []
            for item in module['items']:
                if item['identifierref'] == assignment_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove from organization structure
        for org_module in self.organization_items:
            items_to_remove = []
            for item in org_module['items']:
                if item['identifierref'] == assignment_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                org_module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in org_module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove the physical assignment directory and files if they exist
        if self.output_dir:
            assignment_dir_path = Path(self.output_dir) / assignment_id
            if assignment_dir_path.exists():
                shutil.rmtree(assignment_dir_path)
                print(f"Removed assignment directory: {assignment_id}/")
        
        # Update cartridge state
        self._update_cartridge_state()
        
        print(f"Assignment '{assignment_to_delete['title']}' (ID: {assignment_id}) has been deleted")
        return True

    def delete_quiz_by_id(self, quiz_id):
        """Delete a quiz by its identifier"""
        # Find the quiz in our internal list
        quiz_to_delete = None
        for i, quiz in enumerate(self.quizzes):
            if quiz['identifier'] == quiz_id:
                quiz_to_delete = quiz
                quiz_index = i
                break
        
        if not quiz_to_delete:
            raise ValueError(f"Quiz with identifier {quiz_id} not found")
        
        # Remove from quizzes list
        self.quizzes.pop(quiz_index)
        
        # Remove all related resources (quiz has multiple resource entries)
        resources_to_remove = []
        dependency_ids = []
        
        for resource in self.resources:
            # Find main quiz resource and its dependency
            if resource['identifier'] == quiz_id:
                if 'dependency' in resource:
                    dependency_ids.append(resource['dependency'])
                resources_to_remove.append(resource['identifier'])
            # Find dependency resource  
            elif resource['identifier'] in dependency_ids:
                resources_to_remove.append(resource['identifier'])
        
        # Remove all identified resources
        self.resources = [r for r in self.resources if r['identifier'] not in resources_to_remove]
        
        # Remove from modules and organization items
        for module in self.modules:
            # Find and remove the module item that references this quiz
            items_to_remove = []
            for item in module['items']:
                if item['identifierref'] == quiz_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove from organization structure
        for org_module in self.organization_items:
            items_to_remove = []
            for item in org_module['items']:
                if item['identifierref'] == quiz_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                org_module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in org_module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove the physical quiz directory and files if they exist
        if self.output_dir:
            quiz_dir_path = Path(self.output_dir) / quiz_id
            if quiz_dir_path.exists():
                shutil.rmtree(quiz_dir_path)
                print(f"Removed quiz directory: {quiz_id}/")
            
            # Remove QTI files from non_cc_assessments directory using tracked files
            non_cc_dir = Path(self.output_dir) / "non_cc_assessments"
            if non_cc_dir.exists():
                # Use tracked QTI files if available
                if hasattr(self, 'quiz_qti_files') and quiz_id in self.quiz_qti_files:
                    qti_files_to_remove = self.quiz_qti_files[quiz_id]
                    for qti_filename in qti_files_to_remove:
                        qti_file_path = non_cc_dir / qti_filename
                        if qti_file_path.exists():
                            qti_file_path.unlink()
                            print(f"Removed QTI file: {qti_filename}")
                    # Remove from tracking
                    del self.quiz_qti_files[quiz_id]
                else:
                    # Fallback to old method for backward compatibility
                    qti_files_to_remove = list(non_cc_dir.glob(f"*{quiz_id}*.xml.qti"))
                    
                    # Also check for QTI files that contain the quiz title (for orphaned files)
                    for qti_file in non_cc_dir.glob("*.xml.qti"):
                        try:
                            with open(qti_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if quiz_to_delete['title'] in content and qti_file not in qti_files_to_remove:
                                    qti_files_to_remove.append(qti_file)
                        except:
                            pass  # Skip files that can't be read
                    
                    for qti_file in qti_files_to_remove:
                        qti_file.unlink()
                        print(f"Removed QTI file: {qti_file.name}")
        
        # Update cartridge state
        self._update_cartridge_state()
        
        print(f"Quiz '{quiz_to_delete['title']}' (ID: {quiz_id}) has been deleted")
        return True

    def delete_file_by_id(self, file_id):
        """Delete a file by its identifier (resource ID)"""
        # Find the file in our internal list
        file_to_delete = None
        for i, file_info in enumerate(self.files):
            if file_info['identifier'] == file_id:
                file_to_delete = file_info
                file_index = i
                break
        
        if not file_to_delete:
            raise ValueError(f"File with identifier {file_id} not found")
        
        # Remove from files list
        self.files.pop(file_index)
        
        # Remove from resources list
        self.resources = [r for r in self.resources if r['identifier'] != file_id]
        
        # Remove from modules and organization items
        for module in self.modules:
            # Find and remove the module item that references this file
            items_to_remove = []
            for item in module['items']:
                if item['identifierref'] == file_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove from organization structure
        for org_module in self.organization_items:
            items_to_remove = []
            for item in org_module['items']:
                if item['identifierref'] == file_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                org_module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in org_module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove the physical file if it exists
        if self.output_dir:
            file_path = Path(self.output_dir) / file_to_delete['path']
            if file_path.exists():
                file_path.unlink()
                print(f"Removed file: {file_to_delete['path']}")
        
        # Update cartridge state
        self._update_cartridge_state()
        
        print(f"File '{file_to_delete['filename']}' (ID: {file_id}) has been deleted")
        return True

    def delete_discussion_by_id(self, discussion_id):
        """Delete a discussion by its identifier (main discussion topic ID)"""
        # Find the discussion in our internal list
        discussion_to_delete = None
        for i, discussion in enumerate(self.announcements):
            if discussion['topic_id'] == discussion_id:
                discussion_to_delete = discussion
                discussion_index = i
                break
        
        if not discussion_to_delete:
            raise ValueError(f"Discussion with identifier {discussion_id} not found")
        
        # Remove from announcements list (discussions are stored here)
        self.announcements.pop(discussion_index)
        
        # Remove all related resources (discussion has multiple resource entries like quizzes)
        resources_to_remove = []
        dependency_ids = []
        
        for resource in self.resources:
            # Find main discussion resource and its dependency
            if resource['identifier'] == discussion_id:
                if 'dependency' in resource:
                    dependency_ids.append(resource['dependency'])
                resources_to_remove.append(resource['identifier'])
            # Find dependency resource  
            elif resource['identifier'] in dependency_ids:
                resources_to_remove.append(resource['identifier'])
        
        # Remove all identified resources
        self.resources = [r for r in self.resources if r['identifier'] not in resources_to_remove]
        
        # Remove from modules and organization items
        for module in self.modules:
            # Find and remove the module item that references this discussion
            items_to_remove = []
            for item in module['items']:
                if item['identifierref'] == discussion_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove from organization structure
        for org_module in self.organization_items:
            items_to_remove = []
            for item in org_module['items']:
                if item['identifierref'] == discussion_id:
                    items_to_remove.append(item)
            
            for item in items_to_remove:
                org_module['items'].remove(item)
                # Adjust positions of remaining items
                for remaining_item in org_module['items']:
                    if remaining_item['position'] > item['position']:
                        remaining_item['position'] -= 1
        
        # Remove the physical discussion files if they exist
        if self.output_dir:
            discussions_dir = Path(self.output_dir) / "discussions"
            if discussions_dir.exists():
                # Remove all discussion files that match this discussion ID
                discussion_files_to_remove = list(discussions_dir.glob(f"*{discussion_id}*.xml"))
                
                # Also check for dependency files
                for dep_id in dependency_ids:
                    discussion_files_to_remove.extend(discussions_dir.glob(f"*{dep_id}*.xml"))
                
                for discussion_file in discussion_files_to_remove:
                    discussion_file.unlink()
                    print(f"Removed discussion file: {discussion_file.name}")
        
        # Update cartridge state
        self._update_cartridge_state()
        
        print(f"Discussion '{discussion_to_delete['title']}' (ID: {discussion_id}) has been deleted")
        return True

    def delete_module_by_id(self, module_id):
        """Delete a module and all its contents by its identifier"""
        # Find the module in our internal list
        module_to_delete = None
        for i, module in enumerate(self.modules):
            if module['identifier'] == module_id:
                module_to_delete = module
                module_index = i
                break
        
        if not module_to_delete:
            raise ValueError(f"Module with identifier {module_id} not found")
        
        # Get all items in the module and delete them first
        items_to_delete = []
        for item in module_to_delete['items']:
            items_to_delete.append({
                'identifierref': item['identifierref'],
                'content_type': item['content_type'],
                'title': item['title']
            })
        
        # Delete all module items using existing deletion methods
        for item in items_to_delete:
            try:
                if item['content_type'] == 'WikiPage':
                    self.delete_wiki_page_by_id(item['identifierref'])
                elif item['content_type'] == 'Assignment':
                    self.delete_assignment_by_id(item['identifierref'])
                elif item['content_type'] == 'Quizzes::Quiz':
                    self.delete_quiz_by_id(item['identifierref'])
                elif item['content_type'] == 'DiscussionTopic':
                    self.delete_discussion_by_id(item['identifierref'])
                elif item['content_type'] == 'Attachment':
                    self.delete_file_by_id(item['identifierref'])
                else:
                    print(f"Warning: Unknown content type '{item['content_type']}' for item '{item['title']}'")
            except Exception as e:
                print(f"Warning: Could not delete item '{item['title']}': {e}")
        
        # Now delete the empty module
        # Remove from modules list
        self.modules.pop(module_index)
        
        # Remove from organization structure
        self.organization_items = [org_item for org_item in self.organization_items 
                                 if org_item['identifier'] != module_id]
        
        # Update cartridge state
        self._update_cartridge_state()
        
        print(f"Module '{module_to_delete['title']}' (ID: {module_id}) and all its contents have been deleted")
        return True