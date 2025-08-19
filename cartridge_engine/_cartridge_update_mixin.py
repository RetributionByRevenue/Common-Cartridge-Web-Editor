class CartridgeUpdateMixin:
    """
    Mixin class containing update methods for CartridgeGenerator.
    This mixin provides methods to update various cartridge components by their identifiers.
    """

    def update_wiki(self, wiki_id, page_title=None, page_content=None, published=None, position=None):
        """Update a wiki page's title, content, published status, and/or position by its identifier"""
        # Find the wiki page in our internal list
        wiki_page = None
        for page in self.wiki_pages:
            if page['identifier'] == wiki_id or page['resource_id'] == wiki_id:
                wiki_page = page
                break
        
        if not wiki_page:
            raise ValueError(f"Wiki page with identifier {wiki_id} not found")
        
        # Store old values for comparison
        old_title = wiki_page['title']
        old_content = wiki_page['content']
        old_published = wiki_page['workflow_state'] == 'published'
        old_position = None
        
        # Find the wiki page's position in modules if it exists
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == wiki_page['resource_id']:
                    old_position = item['position']
                    break
        
        # Update the wiki page properties
        if page_title is not None:
            old_filename = wiki_page['filename']
            wiki_page['title'] = page_title
            # Update filename to match new title
            new_filename = f"wiki_content/{page_title.lower().replace(' ', '-').replace('_', '-')}.html"
            wiki_page['filename'] = new_filename
            
            # Also update the corresponding resource's href
            for resource in self.resources:
                if resource['identifier'] == wiki_page['resource_id']:
                    resource['href'] = new_filename
                    break
            
            # Rename the file on disk if filename changed
            if self.output_dir and old_filename != new_filename:
                import os
                from pathlib import Path
                old_file_path = os.path.join(self.output_dir, old_filename)
                new_file_path = Path(self.output_dir) / new_filename
                if os.path.exists(old_file_path):
                    os.rename(old_file_path, new_file_path)
                    # Update the content with the new title
                    self._create_wiki_page_html(new_file_path, wiki_page)
        
        if page_content is not None:
            wiki_page['content'] = page_content
            
            # Write the content directly to the file if we have output_dir
            if self.output_dir:
                import os
                from pathlib import Path
                file_path = Path(self.output_dir) / wiki_page['filename']
                self._create_wiki_page_html(file_path, wiki_page)
        
        if published is not None:
            wiki_page['workflow_state'] = 'published' if published else 'unpublished'
        
        # Update position if specified and wiki page is part of a module
        if position is not None and old_position is not None:
            # Find the module containing this wiki page
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == wiki_page['resource_id']:
                        # Remove item from current position
                        module['items'].remove(item)
                        
                        # Adjust positions of items after the removed item
                        for remaining_item in module['items']:
                            if remaining_item['position'] > old_position:
                                remaining_item['position'] -= 1
                        
                        # Clamp new position to valid range
                        min_position = 1
                        max_position = len(module['items']) + 1
                        new_position = max(min_position, min(position, max_position))
                        
                        # Adjust positions of existing items if inserting at specific position
                        for existing_item in module['items']:
                            if existing_item['position'] >= new_position:
                                existing_item['position'] += 1
                        
                        # Set new position and re-add item
                        item['position'] = new_position
                        module['items'].append(item)
                        
                        # Also update organization items
                        for org_module in self.organization_items:
                            if org_module['identifier'] == module['identifier']:
                                for org_item in org_module['items']:
                                    if org_item['identifierref'] == wiki_page['resource_id']:
                                        org_item['position'] = new_position
                                        break
                        break
        
        # Update references in modules and organization items
        if page_title is not None and page_title != old_title:
            # Update module items
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == wiki_page['resource_id']:
                        item['title'] = page_title
                        if published is not None:
                            item['workflow_state'] = 'published' if published else 'unpublished'
            
            # Update organization items
            for org_module in self.organization_items:
                for item in org_module['items']:
                    if item['identifierref'] == wiki_page['resource_id']:
                        item['title'] = page_title
        elif published is not None:
            # Update workflow state in modules if only published status changed
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == wiki_page['resource_id']:
                        item['workflow_state'] = 'published' if published else 'unpublished'
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        # Build update message
        updates = []
        if page_title is not None and page_title != old_title:
            updates.append(f"title: '{old_title}' → '{page_title}'")
        if page_content is not None and page_content != old_content:
            updates.append(f"content updated")
        if published is not None and published != old_published:
            updates.append(f"published: {old_published} → {published}")
        if position is not None and position != old_position:
            if old_position is not None:
                updates.append(f"position: {old_position} → {position}")
            else:
                updates.append(f"position: not in module → {position} (ignored - not in module)")
        
        if updates:
            update_msg = ", ".join(updates)
            print(f"Wiki page '{wiki_page['title']}' (ID: {wiki_id}) updated: {update_msg}")
        else:
            print(f"Wiki page '{wiki_page['title']}' (ID: {wiki_id}) - no changes made")
        
        return True

    def update_assignment(self, assignment_id, assignment_title=None, assignment_content=None, points=None, published=None, position=None):
        """Update an assignment's title, content, points, published status, and/or position by its identifier"""
        # Find the assignment in our internal list
        assignment = None
        for assign in self.assignments:
            if assign['identifier'] == assignment_id:
                assignment = assign
                break
        
        if not assignment:
            raise ValueError(f"Assignment with identifier {assignment_id} not found")
        
        # Store old values for comparison
        old_title = assignment['title']
        old_content = assignment['content']
        old_points = assignment['points_possible']
        old_published = assignment['workflow_state'] == 'published'
        old_position = None
        
        # Find the assignment's position in modules if it exists
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == assignment_id:
                    old_position = item['position']
                    break
        
        # Update the assignment properties
        if assignment_title is not None:
            assignment['title'] = assignment_title
        
        if assignment_content is not None:
            assignment['content'] = assignment_content
        
        if points is not None:
            assignment['points_possible'] = points
        
        if published is not None:
            assignment['workflow_state'] = 'published' if published else 'unpublished'
        
        # Write the content directly to files if we have output_dir and any content changed
        if self.output_dir and (assignment_title is not None or assignment_content is not None or points is not None or published is not None):
            from pathlib import Path
            assignment_dir = Path(self.output_dir) / assignment['identifier']
            if assignment_dir.exists():
                self._create_assignment_files(Path(self.output_dir), assignment)
        
        # Update position if specified and assignment is part of a module
        if position is not None and old_position is not None:
            # Find the module containing this assignment
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == assignment_id:
                        # Remove item from current position
                        module['items'].remove(item)
                        
                        # Adjust positions of items after the removed item
                        for remaining_item in module['items']:
                            if remaining_item['position'] > old_position:
                                remaining_item['position'] -= 1
                        
                        # Clamp new position to valid range
                        min_position = 1
                        max_position = len(module['items']) + 1
                        new_position = max(min_position, min(position, max_position))
                        
                        # Adjust positions of existing items if inserting at specific position
                        for existing_item in module['items']:
                            if existing_item['position'] >= new_position:
                                existing_item['position'] += 1
                        
                        # Set new position and re-add item
                        item['position'] = new_position
                        module['items'].append(item)
                        
                        # Also update organization items
                        for org_module in self.organization_items:
                            if org_module['identifier'] == module['identifier']:
                                for org_item in org_module['items']:
                                    if org_item['identifierref'] == assignment_id:
                                        org_item['position'] = new_position
                                        break
                        break
        
        # Update references in modules and organization items
        if assignment_title is not None and assignment_title != old_title:
            # Update module items
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == assignment_id:
                        item['title'] = assignment_title
                        if published is not None:
                            item['workflow_state'] = 'published' if published else 'unpublished'
            
            # Update organization items
            for org_module in self.organization_items:
                for item in org_module['items']:
                    if item['identifierref'] == assignment_id:
                        item['title'] = assignment_title
        elif published is not None:
            # Update workflow state in modules if only published status changed
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == assignment_id:
                        item['workflow_state'] = 'published' if published else 'unpublished'
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        # Build update message
        updates = []
        if assignment_title is not None and assignment_title != old_title:
            updates.append(f"title: '{old_title}' → '{assignment_title}'")
        if assignment_content is not None and assignment_content != old_content:
            updates.append(f"content updated")
        if points is not None and points != old_points:
            updates.append(f"points: {old_points} → {points}")
        if published is not None and published != old_published:
            updates.append(f"published: {old_published} → {published}")
        if position is not None and position != old_position:
            if old_position is not None:
                updates.append(f"position: {old_position} → {position}")
            else:
                updates.append(f"position: not in module → {position} (ignored - not in module)")
        
        if updates:
            update_msg = ", ".join(updates)
            print(f"Assignment '{assignment['title']}' (ID: {assignment_id}) updated: {update_msg}")
        else:
            print(f"Assignment '{assignment['title']}' (ID: {assignment_id}) - no changes made")
        
        return True

    def update_quiz(self, quiz_id, quiz_title=None, quiz_description=None, points=None, published=None, position=None):
        """Update a quiz's title, description, points, published status, and/or position by its identifier"""
        # Find the quiz in our internal list
        quiz = None
        for q in self.quizzes:
            if q['identifier'] == quiz_id:
                quiz = q
                break
        
        if not quiz:
            raise ValueError(f"Quiz with identifier {quiz_id} not found")
        
        # Store old values for comparison
        old_title = quiz['title']
        old_description = quiz['description']
        old_points = quiz['points_possible']
        old_published = quiz['workflow_state'] == 'published'
        old_position = None
        
        # Find the quiz's position in modules if it exists
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == quiz_id:
                    old_position = item['position']
                    break
        
        # Update the quiz properties
        if quiz_title is not None:
            quiz['title'] = quiz_title
        
        if quiz_description is not None:
            quiz['description'] = quiz_description
        
        if points is not None:
            quiz['points_possible'] = points
        
        if published is not None:
            quiz['workflow_state'] = 'published' if published else 'unpublished'
        
        # Update position if specified and quiz is part of a module
        if position is not None and old_position is not None:
            # Find the module containing this quiz
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == quiz_id:
                        # Remove item from current position
                        module['items'].remove(item)
                        
                        # Adjust positions of items after the removed item
                        for remaining_item in module['items']:
                            if remaining_item['position'] > old_position:
                                remaining_item['position'] -= 1
                        
                        # Clamp new position to valid range
                        min_position = 1
                        max_position = len(module['items']) + 1
                        new_position = max(min_position, min(position, max_position))
                        
                        # Adjust positions of existing items if inserting at specific position
                        for existing_item in module['items']:
                            if existing_item['position'] >= new_position:
                                existing_item['position'] += 1
                        
                        # Set new position and re-add item
                        item['position'] = new_position
                        module['items'].append(item)
                        
                        # Also update organization items
                        for org_module in self.organization_items:
                            if org_module['identifier'] == module['identifier']:
                                for org_item in org_module['items']:
                                    if org_item['identifierref'] == quiz_id:
                                        org_item['position'] = new_position
                                        break
                        break
        
        # Update references in modules and organization items
        if quiz_title is not None and quiz_title != old_title:
            # Update module items
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == quiz_id:
                        item['title'] = quiz_title
                        if published is not None:
                            item['workflow_state'] = 'published' if published else 'unpublished'
            
            # Update organization items
            for org_module in self.organization_items:
                for item in org_module['items']:
                    if item['identifierref'] == quiz_id:
                        item['title'] = quiz_title
        elif published is not None:
            # Update workflow state in modules if only published status changed
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == quiz_id:
                        item['workflow_state'] = 'published' if published else 'unpublished'
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        # Build update message
        updates = []
        if quiz_title is not None and quiz_title != old_title:
            updates.append(f"title: '{old_title}' → '{quiz_title}'")
        if quiz_description is not None and quiz_description != old_description:
            updates.append(f"description updated")
        if points is not None and points != old_points:
            updates.append(f"points: {old_points} → {points}")
        if published is not None and published != old_published:
            updates.append(f"published: {old_published} → {published}")
        if position is not None and position != old_position:
            if old_position is not None:
                updates.append(f"position: {old_position} → {position}")
            else:
                updates.append(f"position: not in module → {position} (ignored - not in module)")
        
        if updates:
            update_msg = ", ".join(updates)
            print(f"Quiz '{quiz['title']}' (ID: {quiz_id}) updated: {update_msg}")
        else:
            print(f"Quiz '{quiz['title']}' (ID: {quiz_id}) - no changes made")
        
        return True

    def update_discussion(self, discussion_id, title=None, body=None, published=None, position=None):
        """Update a discussion's title, body, published status, and/or position by its identifier"""
        # Find the discussion in our internal list (discussions are stored in announcements)
        discussion = None
        for disc in self.announcements:
            if disc['topic_id'] == discussion_id:
                discussion = disc
                break
        
        if not discussion:
            raise ValueError(f"Discussion with identifier {discussion_id} not found")
        
        # Store old values for comparison
        old_title = discussion['title']
        old_body = discussion.get('body', discussion.get('content', ''))
        old_published = discussion['workflow_state'] == 'active'
        old_position = None
        
        # Find the discussion's position in modules if it exists
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == discussion_id:
                    old_position = item['position']
                    break
        
        # Update the discussion properties
        if title is not None:
            discussion['title'] = title
        
        if body is not None:
            # Handle both 'body' and 'content' fields for compatibility
            if 'body' in discussion:
                discussion['body'] = body
            else:
                discussion['content'] = body
        
        if published is not None:
            discussion['workflow_state'] = 'active' if published else 'unpublished'
        
        # Update position if specified and discussion is part of a module
        if position is not None and old_position is not None:
            # Find the module containing this discussion
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == discussion_id:
                        # Remove item from current position
                        module['items'].remove(item)
                        
                        # Adjust positions of items after the removed item
                        for remaining_item in module['items']:
                            if remaining_item['position'] > old_position:
                                remaining_item['position'] -= 1
                        
                        # Clamp new position to valid range
                        min_position = 1
                        max_position = len(module['items']) + 1
                        new_position = max(min_position, min(position, max_position))
                        
                        # Adjust positions of existing items if inserting at specific position
                        for existing_item in module['items']:
                            if existing_item['position'] >= new_position:
                                existing_item['position'] += 1
                        
                        # Set new position and re-add item
                        item['position'] = new_position
                        module['items'].append(item)
                        
                        # Also update organization items
                        for org_module in self.organization_items:
                            if org_module['identifier'] == module['identifier']:
                                for org_item in org_module['items']:
                                    if org_item['identifierref'] == discussion_id:
                                        org_item['position'] = new_position
                                        break
                        break
        
        # Update references in modules and organization items
        if title is not None and title != old_title:
            # Update module items
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == discussion_id:
                        item['title'] = title
                        if published is not None:
                            item['workflow_state'] = 'published' if published else 'unpublished'
            
            # Update organization items
            for org_module in self.organization_items:
                for item in org_module['items']:
                    if item['identifierref'] == discussion_id:
                        item['title'] = title
        elif published is not None:
            # Update workflow state in modules if only published status changed
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == discussion_id:
                        item['workflow_state'] = 'published' if published else 'unpublished'
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        # Build update message
        updates = []
        if title is not None and title != old_title:
            updates.append(f"title: '{old_title}' → '{title}'")
        if body is not None and body != old_body:
            updates.append(f"body updated")
        if published is not None and published != old_published:
            updates.append(f"published: {old_published} → {published}")
        if position is not None and position != old_position:
            if old_position is not None:
                updates.append(f"position: {old_position} → {position}")
            else:
                updates.append(f"position: not in module → {position} (ignored - not in module)")
        
        if updates:
            update_msg = ", ".join(updates)
            print(f"Discussion '{discussion['title']}' (ID: {discussion_id}) updated: {update_msg}")
        else:
            print(f"Discussion '{discussion['title']}' (ID: {discussion_id}) - no changes made")
        
        return True

    def update_file(self, file_id, filename=None, file_content=None, position=None):
        """Update a file's filename, content, and/or position by its identifier"""
        # Find the file in our internal list
        file_info = None
        for file_obj in self.files:
            if file_obj['identifier'] == file_id:
                file_info = file_obj
                break
        
        if not file_info:
            raise ValueError(f"File with identifier {file_id} not found")
        
        # Store old values for comparison
        old_filename = file_info['filename']
        old_content = file_info['content']
        old_position = None
        
        # Find the file's position in modules if it exists
        for module in self.modules:
            for item in module['items']:
                if item['identifierref'] == file_id:
                    old_position = item['position']
                    break
        
        # Update the file properties
        if filename is not None:
            old_path = file_info['path']
            file_info['filename'] = filename
            # Update path to match new filename
            new_path = f"web_resources/{filename}"
            file_info['path'] = new_path
            
            # Rename the file on disk if filename changed
            if self.output_dir and old_path != new_path:
                import os
                from pathlib import Path
                old_file_path = os.path.join(self.output_dir, old_path)
                new_file_path = os.path.join(self.output_dir, new_path)
                if os.path.exists(old_file_path):
                    # Ensure new directory exists
                    Path(new_file_path).parent.mkdir(parents=True, exist_ok=True)
                    os.rename(old_file_path, new_file_path)
        
        if file_content is not None:
            file_info['content'] = file_content
            
            # Write the content directly to the file if we have output_dir
            if self.output_dir:
                from pathlib import Path
                file_path = Path(self.output_dir) / file_info['path']
                self._create_web_resource_file(Path(self.output_dir), file_info)
        
        # Update filename references in modules and organization items
        if filename is not None and filename != old_filename:
            # Update module items
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == file_id:
                        item['title'] = filename
        
            # Update organization items
            for org_module in self.organization_items:
                for item in org_module['items']:
                    if item['identifierref'] == file_id:
                        item['title'] = filename
        
        # Update position if specified
        if position is not None and old_position is not None:
            # Find the module containing this file
            for module in self.modules:
                for item in module['items']:
                    if item['identifierref'] == file_id:
                        # Remove item from current position
                        module['items'].remove(item)
                        
                        # Adjust positions of items after the removed item
                        for remaining_item in module['items']:
                            if remaining_item['position'] > old_position:
                                remaining_item['position'] -= 1
                        
                        # Clamp new position to valid range
                        min_position = 1
                        max_position = len(module['items']) + 1
                        new_position = max(min_position, min(position, max_position))
                        
                        # Adjust positions of existing items if inserting at specific position
                        for existing_item in module['items']:
                            if existing_item['position'] >= new_position:
                                existing_item['position'] += 1
                        
                        # Set new position and re-add item
                        item['position'] = new_position
                        module['items'].append(item)
                        
                        # Also update organization items
                        for org_module in self.organization_items:
                            if org_module['identifier'] == module['identifier']:
                                for org_item in org_module['items']:
                                    if org_item['identifierref'] == file_id:
                                        org_item['position'] = new_position
                                        break
                        break
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        # Build update message
        updates = []
        if filename is not None and filename != old_filename:
            updates.append(f"filename: '{old_filename}' → '{filename}'")
        if file_content is not None and file_content != old_content:
            updates.append(f"content updated")
        if position is not None and position != old_position:
            if old_position is not None:
                updates.append(f"position: {old_position} → {position}")
            else:
                updates.append(f"position: not in module → {position} (ignored - not in module)")
        
        if updates:
            update_msg = ", ".join(updates)
            print(f"File '{file_info['filename']}' (ID: {file_id}) updated: {update_msg}")
        else:
            print(f"File '{file_info['filename']}' (ID: {file_id}) - no changes made")
        
        return True

    def update_module_with_position(self, module_id, new_title=None, new_position=None):
        """Update a module's title and/or position by its identifier"""
        # Find the module in our internal list
        module_to_update = None
        for module in self.modules:
            if module['identifier'] == module_id:
                module_to_update = module
                break
        
        if not module_to_update:
            raise ValueError(f"Module with identifier {module_id} not found")
        
        # Store old values for comparison
        old_title = module_to_update['title']
        old_position = module_to_update['position']
        
        # Track what we're updating
        updates = []
        
        # Update title if provided
        if new_title is not None and new_title != old_title:
            module_to_update['title'] = new_title
            updates.append(f"title: '{old_title}' → '{new_title}'")
            
            # Update title in organization items as well
            for org_module in self.organization_items:
                if org_module['identifier'] == module_id:
                    org_module['title'] = new_title
                    break
        
        # Update position if provided
        if new_position is not None and new_position != old_position:
            # Clamp position to valid range (1-based indexing, no gaps allowed)
            min_position = 1
            max_position = len(self.modules)
            clamped_position = max(min_position, min(new_position, max_position))
            
            # If position was clamped, update the message and use clamped position
            position_was_clamped = (clamped_position != new_position)
            if position_was_clamped:
                updates.append(f"position: {old_position} → {new_position} (clamped to {clamped_position})")
                new_position = clamped_position
            
            # First, adjust positions of other modules
            if new_position < old_position:
                # Moving module to earlier position - shift modules between new_position and old_position forward
                for other_module in self.modules:
                    if other_module['identifier'] != module_id:
                        other_pos = other_module['position']
                        if new_position <= other_pos < old_position:
                            other_module['position'] += 1
            elif new_position > old_position:
                # Moving module to later position - shift modules between old_position and new_position backward
                for other_module in self.modules:
                    if other_module['identifier'] != module_id:
                        other_pos = other_module['position']
                        if old_position < other_pos <= new_position:
                            other_module['position'] -= 1
            
            # Set new position for this module
            module_to_update['position'] = new_position
            
            # Add position update message only if position wasn't clamped
            if not position_was_clamped:
                updates.append(f"position: {old_position} → {new_position}")
        
        # Update cartridge state to regenerate files
        self._update_cartridge_state()
        
        # Build update message
        if updates:
            update_msg = ", ".join(updates)
            print(f"✓ Module '{module_to_update['title']}' (ID: {module_id}) updated: {update_msg}")
        else:
            print(f"Module '{module_to_update['title']}' (ID: {module_id}) - no changes made")
        
        return True