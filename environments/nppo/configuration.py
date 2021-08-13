REPOSITORY = "870512711545.dkr.ecr.eu-central-1.amazonaws.com"
REPOSITORY_AWS_PROFILE = "nppo-prod"


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
    }
