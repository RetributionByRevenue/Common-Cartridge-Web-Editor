import uuid


class CartridgeCopyMixin:
    """
    Mixin class containing copy methods for CartridgeGenerator.
    This mixin provides methods to copy various content types either as standalone items
    or to specific modules within the cartridge.
    """

    def copy_wiki_page(self, wiki_page_id, module_id=None):
        """Copy a wiki page to another module or as standalone by providing the wiki page id and optional module id"""
        # Find the original wiki page
        original_page = None
        for page in self.wiki_pages:
            if page['identifier'] == wiki_page_id or page['resource_id'] == wiki_page_id:
                original_page = page
                break
        
        if not original_page:
            raise ValueError(f"Wiki page with identifier {wiki_page_id} not found")
        
        # Generate new IDs for the copy
        new_page_id = f"g{uuid.uuid4().hex}"
        new_resource_id = f"g{uuid.uuid4().hex}"
        
        # Create copy with new title to indicate it's a copy
        copy_title = f"{original_page['title']} (Copy)"
        
        if module_id is None:
            # Add as standalone wiki page (similar to add_wiki_page_standalone)
            wiki_page_copy = {
                'identifier': new_page_id,
                'resource_id': new_resource_id,
                'title': copy_title,
                'content': original_page['content'],
                'workflow_state': original_page['workflow_state'],
                'filename': f"wiki_content/{copy_title.lower().replace(' ', '-').replace('_', '-')}.html"
            }
            self.wiki_pages.append(wiki_page_copy)
            
            # Add to resources (but not to organization structure)
            self.resources.append({
                'identifier': new_resource_id,
                'type': 'webcontent',
                'href': wiki_page_copy['filename']
            })
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_page_id
        else:
            # Add to specific module (similar to add_wiki_page_to_module)
            item_id = f"g{uuid.uuid4().hex}"
            
            # Find the module in both internal list and verify it exists
            target_module = None
            for module in self.modules:
                if module['identifier'] == module_id:
                    target_module = module
                    break
            
            if not target_module:
                raise ValueError(f"Module with identifier {module_id} not found")
            
            # Determine position for the new item
            item_position = len(target_module['items']) + 1
            
            # Create module item
            item = {
                'identifier': item_id,
                'title': copy_title,
                'content_type': 'WikiPage',
                'workflow_state': original_page['workflow_state'],
                'identifierref': new_resource_id,
                'position': item_position
            }
            target_module['items'].append(item)
            
            # Store wiki page info
            wiki_page_copy = {
                'identifier': new_page_id,
                'resource_id': new_resource_id,
                'title': copy_title,
                'content': original_page['content'],
                'workflow_state': original_page['workflow_state'],
                'filename': f"wiki_content/{copy_title.lower().replace(' ', '-').replace('_', '-')}.html"
            }
            self.wiki_pages.append(wiki_page_copy)
            
            # Add to resources
            self.resources.append({
                'identifier': new_resource_id,
                'type': 'webcontent',
                'href': wiki_page_copy['filename']
            })
            
            # Add to organization structure
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                org_item = {
                    'identifier': item_id,
                    'title': copy_title,
                    'identifierref': new_resource_id,
                    'position': item_position
                }
                org_module['items'].append(org_item)
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_page_id

    def copy_assignment(self, assignment_id, module_id=None):
        """Copy an assignment to another module or as standalone by providing the assignment id and optional module id"""
        # Find the original assignment
        original_assignment = None
        for assignment in self.assignments:
            if assignment['identifier'] == assignment_id:
                original_assignment = assignment
                break
        
        if not original_assignment:
            raise ValueError(f"Assignment with identifier {assignment_id} not found")
        
        # Generate new ID for the copy
        new_assignment_id = f"g{uuid.uuid4().hex}"
        
        # Create copy with new title to indicate it's a copy
        copy_title = f"{original_assignment['title']} (Copy)"
        
        if module_id is None:
            # Add as standalone assignment (similar to add_assignment_standalone)
            assignment_copy = {
                'identifier': new_assignment_id,
                'title': copy_title,
                'content': original_assignment['content'],
                'points_possible': original_assignment['points_possible'],
                'workflow_state': original_assignment['workflow_state'],
                'assignment_group_id': self.assignment_group_id,
                'position': len(self.assignments) + 1
            }
            self.assignments.append(assignment_copy)
            
            # Add to resources (but not to organization structure)
            self.resources.append({
                'identifier': new_assignment_id,
                'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
                'href': f"{new_assignment_id}/my-first-assignment.html"
            })
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_assignment_id
        else:
            # Add to specific module (similar to add_assignment_to_module)
            item_id = f"g{uuid.uuid4().hex}"
            
            # Find the module in both internal list and verify it exists
            target_module = None
            for module in self.modules:
                if module['identifier'] == module_id:
                    target_module = module
                    break
            
            if not target_module:
                # If not found in internal list, check if it exists in current DataFrame
                if self.current_df is not None:
                    module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                       (self.current_df['identifier'] == module_id)].empty
                    if module_exists:
                        # Get module title from DataFrame to create new internal module entry
                        module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                      (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                        # Create internal module entry
                        target_module = {
                            'identifier': module_id,
                            'title': module_title,
                            'position': len(self.modules) + 1,
                            'workflow_state': 'unpublished',
                            'items': []
                        }
                        self.modules.append(target_module)
                        
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
            
            # Determine position for the new item
            item_position = len(target_module['items']) + 1
            
            # Create module item
            item = {
                'identifier': item_id,
                'title': copy_title,
                'content_type': 'Assignment',
                'workflow_state': original_assignment['workflow_state'],
                'identifierref': new_assignment_id,
                'position': item_position
            }
            target_module['items'].append(item)
            
            # Store assignment info
            assignment_copy = {
                'identifier': new_assignment_id,
                'title': copy_title,
                'content': original_assignment['content'],
                'points_possible': original_assignment['points_possible'],
                'workflow_state': original_assignment['workflow_state'],
                'assignment_group_id': self.assignment_group_id,
                'position': len(self.assignments) + 1
            }
            self.assignments.append(assignment_copy)
            
            # Add to resources
            self.resources.append({
                'identifier': new_assignment_id,
                'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
                'href': f"{new_assignment_id}/my-first-assignment.html"
            })
            
            # Add to organization structure
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                org_item = {
                    'identifier': item_id,
                    'title': copy_title,
                    'identifierref': new_assignment_id,
                    'position': item_position
                }
                org_module['items'].append(org_item)
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_assignment_id

    def copy_quiz(self, quiz_id, module_id=None):
        """Copy a quiz to another module or as standalone by providing the quiz id and optional module id"""
        # Find the original quiz
        original_quiz = None
        for quiz in self.quizzes:
            if quiz['identifier'] == quiz_id:
                original_quiz = quiz
                break
        
        if not original_quiz:
            raise ValueError(f"Quiz with identifier {quiz_id} not found")
        
        # Generate new IDs for the copy (quizzes need multiple IDs)
        new_quiz_id = f"g{uuid.uuid4().hex}"
        new_assignment_id = f"g{uuid.uuid4().hex}"
        new_resource_id = f"g{uuid.uuid4().hex}"
        new_question_id = f"g{uuid.uuid4().hex}"
        new_assessment_question_id = f"g{uuid.uuid4().hex}"
        
        # Create copy with new title to indicate it's a copy
        copy_title = f"{original_quiz['title']} (Copy)"
        
        if module_id is None:
            # Add as standalone quiz (similar to add_quiz_standalone)
            quiz_copy = {
                'identifier': new_quiz_id,
                'title': copy_title,
                'description': original_quiz['description'],
                'points_possible': original_quiz['points_possible'],
                'workflow_state': original_quiz['workflow_state'],
                'assignment_id': new_assignment_id,
                'assignment_group_id': self.assignment_group_id,
                'position': len(self.quizzes) + 1,
                'question_id': new_question_id,
                'assessment_question_id': new_assessment_question_id
            }
            self.quizzes.append(quiz_copy)
            
            # Add to resources (but not to organization structure)
            self.resources.append({
                'identifier': new_quiz_id,
                'type': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
                'href': f"{new_quiz_id}/assessment_qti.xml",
                'dependency': new_resource_id
            })
            
            self.resources.append({
                'identifier': new_resource_id,
                'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
                'href': f"{new_quiz_id}/assessment_meta.xml"
            })
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_quiz_id
        else:
            # Add to specific module (similar to add_quiz_to_module)
            item_id = f"g{uuid.uuid4().hex}"
            
            # Find the module in both internal list and verify it exists
            target_module = None
            for module in self.modules:
                if module['identifier'] == module_id:
                    target_module = module
                    break
            
            if not target_module:
                # If not found in internal list, check if it exists in current DataFrame
                if self.current_df is not None:
                    module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                       (self.current_df['identifier'] == module_id)].empty
                    if module_exists:
                        # Get module title from DataFrame to create new internal module entry
                        module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                      (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                        # Create internal module entry
                        target_module = {
                            'identifier': module_id,
                            'title': module_title,
                            'position': len(self.modules) + 1,
                            'workflow_state': 'unpublished',
                            'items': []
                        }
                        self.modules.append(target_module)
                        
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
            
            # Determine position for the new item
            item_position = len(target_module['items']) + 1
            
            # Create module item
            item = {
                'identifier': item_id,
                'title': copy_title,
                'content_type': 'Quizzes::Quiz',
                'workflow_state': original_quiz['workflow_state'],
                'identifierref': new_quiz_id,
                'position': item_position
            }
            target_module['items'].append(item)
            
            # Store quiz info
            quiz_copy = {
                'identifier': new_quiz_id,
                'title': copy_title,
                'description': original_quiz['description'],
                'points_possible': original_quiz['points_possible'],
                'workflow_state': original_quiz['workflow_state'],
                'assignment_id': new_assignment_id,
                'assignment_group_id': self.assignment_group_id,
                'position': len(self.quizzes) + 1,
                'question_id': new_question_id,
                'assessment_question_id': new_assessment_question_id
            }
            self.quizzes.append(quiz_copy)
            
            # Add to resources
            self.resources.append({
                'identifier': new_quiz_id,
                'type': 'imsqti_xmlv1p2/imscc_xmlv1p1/assessment',
                'href': f"{new_quiz_id}/assessment_qti.xml",
                'dependency': new_resource_id
            })
            
            self.resources.append({
                'identifier': new_resource_id,
                'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
                'href': f"{new_quiz_id}/assessment_meta.xml"
            })
            
            # Add to organization structure
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                org_item = {
                    'identifier': item_id,
                    'title': copy_title,
                    'identifierref': new_quiz_id,
                    'position': item_position
                }
                org_module['items'].append(org_item)
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_quiz_id

    def copy_discussion(self, discussion_id, module_id=None):
        """Copy a discussion to another module or as standalone by providing the discussion id and optional module id"""
        # Find the original discussion (stored in announcements list)
        original_discussion = None
        for discussion in self.announcements:
            if discussion['topic_id'] == discussion_id or discussion['meta_id'] == discussion_id:
                original_discussion = discussion
                break
        
        if not original_discussion:
            raise ValueError(f"Discussion with identifier {discussion_id} not found")
        
        # Generate new IDs for the copy
        new_topic_id = f"g{uuid.uuid4().hex}"
        new_meta_id = f"g{uuid.uuid4().hex}"
        
        # Create copy with new title to indicate it's a copy
        copy_title = f"{original_discussion['title']} (Copy)"
        
        if module_id is None:
            # Add as standalone discussion (similar to add_discussion_standalone)
            discussion_copy = {
                'topic_id': new_topic_id,
                'meta_id': new_meta_id,
                'title': copy_title,
                'body': original_discussion['body'],
                'workflow_state': original_discussion['workflow_state']
            }
            self.announcements.append(discussion_copy)
            
            # Add to resources (but not to organization structure)
            self.resources.append({
                'identifier': new_topic_id,
                'type': 'imsdt_xmlv1p1',
                'href': f"{new_topic_id}.xml",
                'dependency': new_meta_id
            })
            
            self.resources.append({
                'identifier': new_meta_id,
                'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
                'href': f"{new_meta_id}.xml"
            })
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_topic_id
        else:
            # Add to specific module (similar to add_discussion_to_module)
            item_id = f"g{uuid.uuid4().hex}"
            
            # Find the module in both internal list and verify it exists
            target_module = None
            for module in self.modules:
                if module['identifier'] == module_id:
                    target_module = module
                    break
            
            if not target_module:
                # If not found in internal list, check if it exists in current DataFrame
                if self.current_df is not None:
                    module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                       (self.current_df['identifier'] == module_id)].empty
                    if module_exists:
                        # Get module title from DataFrame to create new internal module entry
                        module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                      (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                        # Create internal module entry
                        target_module = {
                            'identifier': module_id,
                            'title': module_title,
                            'position': len(self.modules) + 1,
                            'workflow_state': 'unpublished',
                            'items': []
                        }
                        self.modules.append(target_module)
                        
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
            
            # Determine position for the new item
            item_position = len(target_module['items']) + 1
            
            # Create module item
            item = {
                'identifier': item_id,
                'title': copy_title,
                'content_type': 'DiscussionTopic',
                'workflow_state': original_discussion['workflow_state'],
                'identifierref': new_topic_id,
                'position': item_position
            }
            target_module['items'].append(item)
            
            # Store discussion info
            discussion_copy = {
                'topic_id': new_topic_id,
                'meta_id': new_meta_id,
                'title': copy_title,
                'body': original_discussion['body'],
                'workflow_state': original_discussion['workflow_state']
            }
            self.announcements.append(discussion_copy)
            
            # Add to resources
            self.resources.append({
                'identifier': new_topic_id,
                'type': 'imsdt_xmlv1p1',
                'href': f"{new_topic_id}.xml",
                'dependency': new_meta_id
            })
            
            self.resources.append({
                'identifier': new_meta_id,
                'type': 'associatedcontent/imscc_xmlv1p1/learning-application-resource',
                'href': f"{new_meta_id}.xml"
            })
            
            # Add to organization structure
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                org_item = {
                    'identifier': item_id,
                    'title': copy_title,
                    'identifierref': new_topic_id,
                    'position': item_position
                }
                org_module['items'].append(org_item)
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_topic_id

    def copy_file(self, file_id, module_id=None):
        """Copy a file to another module or as standalone by providing the file id and optional module id"""
        # Find the original file
        original_file = None
        for file_info in self.files:
            if file_info['identifier'] == file_id:
                original_file = file_info
                break
        
        if not original_file:
            raise ValueError(f"File with identifier {file_id} not found")
        
        # Generate new ID for the copy
        new_file_id = f"g{uuid.uuid4().hex}"
        
        # Create copy with new filename to indicate it's a copy
        original_filename = original_file['filename']
        filename_parts = original_filename.rsplit('.', 1)
        if len(filename_parts) == 2:
            copy_filename = f"{filename_parts[0]} (Copy).{filename_parts[1]}"
        else:
            copy_filename = f"{original_filename} (Copy)"
        
        if module_id is None:
            # Add as standalone file (similar to add_file_standalone)
            file_copy = {
                'identifier': new_file_id,
                'filename': copy_filename,
                'content': original_file['content'],
                'path': f"web_resources/{copy_filename}"
            }
            self.files.append(file_copy)
            
            # Add to resources (but not to organization structure)
            self.resources.append({
                'identifier': new_file_id,
                'type': 'webcontent',
                'href': f"web_resources/{copy_filename}"
            })
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_file_id
        else:
            # Add to specific module (similar to add_file_to_module)
            item_id = f"g{uuid.uuid4().hex}"
            
            # Find the module in both internal list and verify it exists
            target_module = None
            for module in self.modules:
                if module['identifier'] == module_id:
                    target_module = module
                    break
            
            if not target_module:
                # If not found in internal list, check if it exists in current DataFrame
                if self.current_df is not None:
                    module_exists = not self.current_df[(self.current_df['type'] == 'module') & 
                                                       (self.current_df['identifier'] == module_id)].empty
                    if module_exists:
                        # Get module title from DataFrame to create new internal module entry
                        module_title = self.current_df[(self.current_df['type'] == 'module') & 
                                                      (self.current_df['identifier'] == module_id)]['title'].iloc[0]
                        # Create internal module entry
                        target_module = {
                            'identifier': module_id,
                            'title': module_title,
                            'position': len(self.modules) + 1,
                            'workflow_state': 'unpublished',
                            'items': []
                        }
                        self.modules.append(target_module)
                        
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
            
            # Determine position for the new item
            item_position = len(target_module['items']) + 1
            
            # Create module item
            item = {
                'identifier': item_id,
                'title': copy_filename,
                'content_type': 'Attachment',
                'workflow_state': 'published',
                'identifierref': new_file_id,
                'position': item_position
            }
            target_module['items'].append(item)
            
            # Store file info
            file_copy = {
                'identifier': new_file_id,
                'filename': copy_filename,
                'content': original_file['content'],
                'path': f"web_resources/{copy_filename}"
            }
            self.files.append(file_copy)
            
            # Add to resources
            self.resources.append({
                'identifier': new_file_id,
                'type': 'webcontent',
                'href': f"web_resources/{copy_filename}"
            })
            
            # Add to organization structure
            org_module = next((m for m in self.organization_items if m['identifier'] == module_id), None)
            if org_module:
                org_item = {
                    'identifier': item_id,
                    'title': copy_filename,
                    'identifierref': new_file_id,
                    'position': item_position
                }
                org_module['items'].append(org_item)
            
            # Update cartridge state
            self._update_cartridge_state()
            
            return new_file_id