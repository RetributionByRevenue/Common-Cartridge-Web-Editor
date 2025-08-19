import json

class CartridgeDisplayMixin:
    """
    Mixin class containing display methods for CartridgeGenerator.
    This mixin provides methods to display various cartridge components by their identifiers.
    """

    def display_wiki(self, wiki_id):
        """Display a wiki page's information by its identifier"""
        # Find the wiki page in our internal list
        wiki_page = None
        for page in self.wiki_pages:
            if page['identifier'] == wiki_id or page['resource_id'] == wiki_id:
                wiki_page = page
                break
        
        if not wiki_page:
            raise ValueError(f"Wiki page with identifier {wiki_id} not found")
        
        # Find the wiki page's position in modules if it exists
        position = None
        module_name = None
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == wiki_page['resource_id']:
                    position = item['position']
                    module_name = module['title']
                    break
        
        # Build display information
        display_info = {
            'id': wiki_page['identifier'],
            'resource_id': wiki_page['resource_id'],
            'title': wiki_page['title'],
            'content': wiki_page['content'],
            'filename': wiki_page['filename'],
            'workflow_state': wiki_page['workflow_state'],
            'published': wiki_page['workflow_state'] == 'published',
            'position': position,
            'module': module_name
        }
        
        # Print JSON output
        print(json.dumps(display_info, indent=2))
        
        return display_info

    def display_assignment(self, assignment_id):
        """Display an assignment's information by its identifier"""
        # Find the assignment in our internal list
        assignment = None
        for assign in self.assignments:
            if assign['identifier'] == assignment_id:
                assignment = assign
                break
        
        if not assignment:
            raise ValueError(f"Assignment with identifier {assignment_id} not found")
        
        # Find the assignment's position in modules if it exists
        position = None
        module_name = None
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == assignment_id:
                    position = item['position']
                    module_name = module['title']
                    break
        
        # Build display information
        display_info = {
            'id': assignment['identifier'],
            'title': assignment['title'],
            'content': assignment['content'],
            'points_possible': assignment['points_possible'],
            'workflow_state': assignment['workflow_state'],
            'published': assignment['workflow_state'] == 'published',
            'position': position,
            'module': module_name
        }
        
        # Print JSON output
        print(json.dumps(display_info, indent=2))
        
        return display_info

    def display_quiz(self, quiz_id):
        """Display a quiz's information by its identifier"""
        # Find the quiz in our internal list
        quiz = None
        for q in self.quizzes:
            if q['identifier'] == quiz_id:
                quiz = q
                break
        
        if not quiz:
            raise ValueError(f"Quiz with identifier {quiz_id} not found")
        
        # Find the quiz's position in modules if it exists
        position = None
        module_name = None
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == quiz_id:
                    position = item['position']
                    module_name = module['title']
                    break
        
        # Build display information
        display_info = {
            'id': quiz['identifier'],
            'title': quiz['title'],
            'description': quiz['description'],
            'points_possible': quiz['points_possible'],
            'workflow_state': quiz['workflow_state'],
            'published': quiz['workflow_state'] == 'published',
            'position': position,
            'module': module_name
        }
        
        # Print JSON output
        print(json.dumps(display_info, indent=2))
        
        return display_info

    def display_discussion(self, discussion_id):
        """Display a discussion's information by its identifier"""
        # Find the discussion in our internal list (discussions are stored in announcements)
        discussion = None
        for disc in self.announcements:
            if disc['topic_id'] == discussion_id:
                discussion = disc
                break
        
        if not discussion:
            raise ValueError(f"Discussion with identifier {discussion_id} not found")
        
        # Find the discussion's position in modules if it exists
        position = None
        module_name = None
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == discussion_id:
                    position = item['position']
                    module_name = module['title']
                    break
        
        # Get body content (handle both 'body' and 'content' fields)
        body_content = discussion.get('body', discussion.get('content', ''))
        
        # Build display information
        display_info = {
            'id': discussion['topic_id'],
            'title': discussion['title'],
            'body': body_content,
            'workflow_state': discussion['workflow_state'],
            'published': discussion['workflow_state'] == 'active',
            'position': position,
            'module': module_name
        }
        
        # Print JSON output
        print(json.dumps(display_info, indent=2))
        
        return display_info

    def display_file(self, file_id):
        """Display a file's information by its identifier"""
        # Find the file in our internal list
        file_info = None
        for file_obj in self.files:
            if file_obj['identifier'] == file_id:
                file_info = file_obj
                break
        
        if not file_info:
            raise ValueError(f"File with identifier {file_id} not found")
        
        # Find the file's position in modules if it exists
        position = None
        module_name = None
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == file_id:
                    position = item['position']
                    module_name = module['title']
                    break
        
        # Build display information
        display_info = {
            'id': file_info['identifier'],
            'filename': file_info['filename'],
            'path': file_info['path'],
            'content': file_info['content'],
            'position': position,
            'module': module_name
        }
        
        # Print JSON output
        print(json.dumps(display_info, indent=2))
        
        return display_info