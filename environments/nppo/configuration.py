REPOSITORY = "870512711545.dkr.ecr.eu-central-1.amazonaws.com"
REPOSITORY_AWS_PROFILE = "nppo-prod"
SEARCH_FIELDS = [
    "title^2", "title.analyzed^2", "title.folded^2",
    "text", "text.analyzed", "text.folded",
    "description", "description.analyzed", "description.folded",
    "keywords", "keywords.folded",
    "authors.name.folded",
    "parties.name.folded",
    "projects.name.folded",
]


def get_project_search_mapping_properties():
    return {
        'research_themes': {
            'type': 'keyword'
        },
        'research_object_type': {
            'type': 'keyword'
        },
        'parties': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword',
                            'ignore_above': 256
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                }
            }
        },
        'projects': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'text',
                    'fields': {
                        'keyword': {
                            'type': 'keyword',
                            'ignore_above': 256
                        },
                        'folded': {
                            'type': 'text',
                            'analyzer': 'folding'
                        }
                    }
                }
            }
        },
        'extension': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'text',
                },
                'is_addition': {
                    'type': 'boolean'
                }
            }
        },
    }
