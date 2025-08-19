import uuid


class CartridgeAddMixin:
    """
    Mixin class containing add_*_to_module methods for CartridgeGenerator.
    This mixin provides methods to add various content types to modules in the cartridge.
    """

    def add_wiki_page_to_module(self, module_id, page_title, page_content="", published=True, position=None):
        """Add a wiki page to a specific module using actual module identifier from DataFrame"""
        page_id = f"g{uuid.uuid4().hex}"
        resource_id = f"g{uuid.uuid4().hex}"
        item_id = f"g{uuid.uuid4().hex}"
        
        # Find the module in both internal list and verify it exists in current state
        module = next((m for m in self.modules if m['identifier'] == module_id), None)
        if not module:
            # If not found in internal list, check if it exists in current DataFrame
            if self.current_df is not None:
                module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                   (self.current_df['identifier'] == module_id)].empty
                if module_exists:
                    # Get module title from DataFrame to create new internal module entry
                    module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                  (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                    # Create internal module entry
                    module = {
                        'identifier': module_id,
                        'title': module_title,
                        'position': len(self.modules) + 1,
                        'workflow_state': 'unpublished',
                        'items': []
                    }
                    self.modules.append(module)
                    
                    # Add to organization structure
                    self.organization_items.append({
                        'identifier': module_id,
                        'title': module_title,
                        'type': 'module',
                        'items': []
                    })
                else:
                    raise ValueError(f"Module with identifier {module_id} not found in current cartridge state")
            else:
                raise ValueError(f"Module with identifier {module_id} not found")
        
        # Determine position for new item (1-based indexing, no gaps allowed)
        if position is None:
            item_position = len(module['items']) + 1
        else:
            # Clamp position to valid range (1-based, no gaps)
            min_position = 1
            max_position = len(module['items']) + 1
            item_position = max(min_position, min(position, max_position))
            
            # Adjust positions of existing items if inserting at specific position
            for existing_item in module['items']:
                if existing_item['position'] >= item_position:
                    existing_item['position'] += 1
            
            # Also adjust positions in organization items
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                for org_item in org_module['items']:
                    if org_item['position'] >= item_position:
                        org_item['position'] += 1

        # Add item to module
        item = {
            'identifier': item_id,
            'title': page_title,
            'content_type': 'WikiPage',
            'workflow_state': 'published' if published else 'unpublished',
            'identifierref': resource_id,
            'position': item_position
        }
        module['items'].append(item)
        
        # Store wiki page info
        wiki_page = {
            'identifier': page_id,
            'resource_id': resource_id,
            'title': page_title,
            'content': page_content,
            'workflow_state': 'published' if published else 'unpublished',
            'filename': f"wiki_content/{page_title.lower().replace(' ', '-').replace('_', '-')}.html"
        }
        self.wiki_pages.append(wiki_page)
        
        # Add to resources
        self.resources.append({
            'identifier': resource_id,
            'type': 'webcontent',
            'href': wiki_page['filename']
        })
        
        # Add to organization structure
        org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
        if org_module:
            org_module['items'].append({
                'identifier': item_id,
                'title': page_title,
                'identifierref': resource_id,
                'position': item_position
            })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return page_id

    def add_assignment_to_module(self, module_id, assignment_title, assignment_content="", points=100, published=True, position=None):
        """Add an assignment to a specific module using actual module identifier from DataFrame"""
        assignment_id = f"g{uuid.uuid4().hex}"
        item_id = f"g{uuid.uuid4().hex}"
        
        # Find the module in both internal list and verify it exists in current state
        module = next((m for m in self.modules if m['identifier'] == module_id), None)
        if not module:
            # If not found in internal list, check if it exists in current DataFrame
            if self.current_df is not None:
                module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                   (self.current_df['identifier'] == module_id)].empty
                if module_exists:
                    # Get module title from DataFrame to create new internal module entry
                    module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                  (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                    # Create internal module entry
                    module = {
                        'identifier': module_id,
                        'title': module_title,
                        'position': len(self.modules) + 1,
                        'workflow_state': 'unpublished',
                        'items': []
                    }
                    self.modules.append(module)
                    
                    # Add to organization structure
                    self.organization_items.append({
                        'identifier': module_id,
                        'title': module_title,
                        'type': 'module',
                        'items': []
                    })
                else:
                    raise ValueError(f"Module with identifier {module_id} not found in current cartridge state")
            else:
                raise ValueError(f"Module with identifier {module_id} not found")
        
        # Determine position for new item (1-based indexing, no gaps allowed)
        if position is None:
            item_position = len(module['items']) + 1
        else:
            # Clamp position to valid range (1-based, no gaps)
            min_position = 1
            max_position = len(module['items']) + 1
            item_position = max(min_position, min(position, max_position))
            
            # Adjust positions of existing items if inserting at specific position
            for existing_item in module['items']:
                if existing_item['position'] >= item_position:
                    existing_item['position'] += 1
            
            # Also adjust positions in organization items
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                for org_item in org_module['items']:
                    if org_item['position'] >= item_position:
                        org_item['position'] += 1

        # Add item to module
        item = {
            'identifier': item_id,
            'title': assignment_title,
            'content_type': 'Assignment',
            'workflow_state': 'published' if published else 'unpublished',
            'identifierref': assignment_id,
            'position': item_position
        }
        module['items'].append(item)
        
        # Store assignment info
        assignment = {
            'identifier': assignment_id,
            'title': assignment_title,
            'content': assignment_content,
            'points_possible': points,
            'workflow_state': 'published' if published else 'unpublished',
            'assignment_group_id': self.assignment_group_id,
            'position': len(self.assignments) + 1
        }
        self.assignments.append(assignment)
        
        # Add to resources
        self.resources.append({
            'identifier': assignment_id,
            'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
            'href': f"{assignment_id}/my-first-assignment.html"
        })
        
        # Add to organization structure
        org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
        if org_module:
            org_module['items'].append({
                'identifier': item_id,
                'title': assignment_title,
                'identifierref': assignment_id,
                'position': item_position
            })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return assignment_id

    def add_quiz_to_module(self, module_id, quiz_title, quiz_description="", points=1, published=True, position=None):
        """Add a quiz to a specific module using actual module identifier from DataFrame"""
        quiz_id = f"g{uuid.uuid4().hex}"
        assignment_id = f"g{uuid.uuid4().hex}"
        resource_id = f"g{uuid.uuid4().hex}"
        question_id = f"g{uuid.uuid4().hex}"
        assessment_question_id = f"g{uuid.uuid4().hex}"
        item_id = f"g{uuid.uuid4().hex}"
        
        # Find the module in both internal list and verify it exists in current state
        module = next((m for m in self.modules if m['identifier'] == module_id), None)
        if not module:
            # If not found in internal list, check if it exists in current DataFrame
            if self.current_df is not None:
                module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                   (self.current_df['identifier'] == module_id)].empty
                if module_exists:
                    # Get module title from DataFrame to create new internal module entry
                    module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                  (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                    # Create internal module entry
                    module = {
                        'identifier': module_id,
                        'title': module_title,
                        'position': len(self.modules) + 1,
                        'workflow_state': 'unpublished',
                        'items': []
                    }
                    self.modules.append(module)
                    
                    # Add to organization structure
                    self.organization_items.append({
                        'identifier': module_id,
                        'title': module_title,
                        'type': 'module',
                        'items': []
                    })
                else:
                    raise ValueError(f"Module with identifier {module_id} not found in current cartridge state")
            else:
                raise ValueError(f"Module with identifier {module_id} not found")
        
        # Determine position for new item (1-based indexing, no gaps allowed)
        if position is None:
            item_position = len(module['items']) + 1
        else:
            # Clamp position to valid range (1-based, no gaps)
            min_position = 1
            max_position = len(module['items']) + 1
            item_position = max(min_position, min(position, max_position))
            
            # Adjust positions of existing items if inserting at specific position
            for existing_item in module['items']:
                if existing_item['position'] >= item_position:
                    existing_item['position'] += 1
            
            # Also adjust positions in organization items
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                for org_item in org_module['items']:
                    if org_item['position'] >= item_position:
                        org_item['position'] += 1

        # Add item to module
        item = {
            'identifier': item_id,
            'title': quiz_title,
            'content_type': 'Quizzes::Quiz',
            'workflow_state': 'published' if published else 'unpublished',
            'identifierref': quiz_id,
            'position': item_position
        }
        module['items'].append(item)
        
        # Store quiz info
        quiz = {
            'identifier': quiz_id,
            'title': quiz_title,
            'description': quiz_description,
            'points_possible': points,
            'workflow_state': 'published' if published else 'unpublished',
            'assignment_id': assignment_id,
            'assignment_group_id': self.assignment_group_id,
            'position': len(self.quizzes) + 1,
            'question_id': question_id,
            'assessment_question_id': assessment_question_id
        }
        self.quizzes.append(quiz)
        
        # Add to resources
        self.resources.append({
            'identifier': quiz_id,
            'type': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
            'href': f"{quiz_id}/assessment_qti.xml",
            'dependency': resource_id
        })
        
        self.resources.append({
            'identifier': resource_id,
            'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
            'href': f"{quiz_id}/assessment_meta.xml"
        })
        
        # Add to organization structure
        org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
        if org_module:
            org_module['items'].append({
                'identifier': item_id,
                'title': quiz_title,
                'identifierref': quiz_id,
                'position': item_position
            })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return quiz_id

    def add_discussion_to_module(self, module_id, title, body, published=True, position=None):
        """Add a discussion topic to a specific module using actual module identifier from DataFrame"""
        topic_id = f"g{uuid.uuid4().hex}"
        meta_id = f"g{uuid.uuid4().hex}"
        item_id = f"g{uuid.uuid4().hex}"
        
        # Find the module in both internal list and verify it exists in current state
        module = next((m for m in self.modules if m['identifier'] == module_id), None)
        if not module:
            # If not found in internal list, check if it exists in current DataFrame
            if self.current_df is not None:
                module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                   (self.current_df['identifier'] == module_id)].empty
                if module_exists:
                    # Get module title from DataFrame to create new internal module entry
                    module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                  (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                    # Create internal module entry
                    module = {
                        'identifier': module_id,
                        'title': module_title,
                        'position': len(self.modules) + 1,
                        'workflow_state': 'unpublished',
                        'items': []
                    }
                    self.modules.append(module)
                    
                    # Add to organization structure
                    self.organization_items.append({
                        'identifier': module_id,
                        'title': module_title,
                        'type': 'module',
                        'items': []
                    })
                else:
                    raise ValueError(f"Module with identifier {module_id} not found in current cartridge state")
            else:
                raise ValueError(f"Module with identifier {module_id} not found")
        
        # Determine position for new item (1-based indexing, no gaps allowed)
        if position is None:
            item_position = len(module['items']) + 1
        else:
            # Clamp position to valid range (1-based, no gaps)
            min_position = 1
            max_position = len(module['items']) + 1
            item_position = max(min_position, min(position, max_position))
            
            # Adjust positions of existing items if inserting at specific position
            for existing_item in module['items']:
                if existing_item['position'] >= item_position:
                    existing_item['position'] += 1
            
            # Also adjust positions in organization items
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                for org_item in org_module['items']:
                    if org_item['position'] >= item_position:
                        org_item['position'] += 1

        # Add item to module
        item = {
            'identifier': item_id,
            'title': title,
            'content_type': 'DiscussionTopic',
            'workflow_state': 'published' if published else 'unpublished',
            'identifierref': topic_id,
            'position': item_position
        }
        module['items'].append(item)
        
        # Store discussion topic info
        discussion_topic = {
            'topic_id': topic_id,
            'meta_id': meta_id,
            'title': title,
            'body': body,
            'workflow_state': 'active' if published else 'unpublished',
        }
        self.announcements.append(discussion_topic)
        
        # Add to resources
        self.resources.append({
            'identifier': topic_id,
            'type': 'imsdt_xmlv1p1',
            'href': f"discussions/{topic_id}.xml",
            'dependency': meta_id
        })
        
        self.resources.append({
            'identifier': meta_id,
            'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
            'href': f"discussions/{meta_id}.xml"
        })
        
        # Add to organization structure
        org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
        if org_module:
            org_module['items'].append({
                'identifier': item_id,
                'title': title,
                'identifierref': topic_id,
                'position': item_position
            })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return topic_id

    def add_file_to_module(self, module_id, filename, file_content, position=None):
        """Add a file to a specific module using actual module identifier from DataFrame"""
        file_id = f"g{uuid.uuid4().hex}"
        item_id = f"g{uuid.uuid4().hex}"
        
        # Find the module in both internal list and verify it exists in current state
        module = next((m for m in self.modules if m['identifier'] == module_id), None)
        if not module:
            # If not found in internal list, check if it exists in current DataFrame
            if self.current_df is not None:
                module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                   (self.current_df['identifier'] == module_id)].empty
                if module_exists:
                    # Get module title from DataFrame to create new internal module entry
                    module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                  (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                    # Create internal module entry
                    module = {
                        'identifier': module_id,
                        'title': module_title,
                        'position': len(self.modules) + 1,
                        'workflow_state': 'unpublished',
                        'items': []
                    }
                    self.modules.append(module)
                    
                    # Add to organization structure
                    self.organization_items.append({
                        'identifier': module_id,
                        'title': module_title,
                        'type': 'module',
                        'items': []
                    })
                else:
                    raise ValueError(f"Module with identifier {module_id} not found in current cartridge state")
            else:
                raise ValueError(f"Module with identifier {module_id} not found")
        
        # Determine position for new item (1-based indexing, no gaps allowed)
        if position is None:
            item_position = len(module['items']) + 1
        else:
            # Clamp position to valid range (1-based, no gaps)
            min_position = 1
            max_position = len(module['items']) + 1
            item_position = max(min_position, min(position, max_position))
            
            # Adjust positions of existing items if inserting at specific position
            for existing_item in module['items']:
                if existing_item['position'] >= item_position:
                    existing_item['position'] += 1
            
            # Also adjust positions in organization items
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                for org_item in org_module['items']:
                    if org_item['position'] >= item_position:
                        org_item['position'] += 1

        # Add item to module
        item = {
            'identifier': item_id,
            'title': filename,
            'content_type': 'Attachment',
            'workflow_state': 'published',
            'identifierref': file_id,
            'position': item_position
        }
        module['items'].append(item)
        
        # Store file info
        file_info = {
            'identifier': file_id,
            'filename': filename,
            'content': file_content,
            'path': f"web_resources/{filename}"
        }
        self.files.append(file_info)
        
        # Add to resources
        self.resources.append({
            'identifier': file_id,
            'type': 'webcontent',
            'href': f"web_resources/{filename}"
        })
        
        # Add to organization structure
        org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
        if org_module:
            org_module['items'].append({
                'identifier': item_id,
                'title': filename,
                'identifierref': file_id,
                'position': item_position
            })
        
        # Update cartridge state
        self._update_cartridge_state()
        
        return file_id