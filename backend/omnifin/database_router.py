"""
Database router for Omnifin to handle multiple databases:
- Default database for user management, authentication, orders, analytics
- Knowledge database for AI training data, prompts, group-specific knowledge
"""

class DatabaseRouter:
    """
    A router to control all database operations on models in different databases.
    """
    
    def db_for_read(self, model, **hints):
        """
        Attempts to read knowledge models go to knowledge database.
        """
        if model._meta.app_label == 'knowledge':
            return 'knowledge'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Attempts to write knowledge models go to knowledge database.
        """
        if model._meta.app_label == 'knowledge':
            return 'knowledge'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the knowledge app is involved.
        """
        if obj1._meta.app_label == 'knowledge' or obj2._meta.app_label == 'knowledge':
            return True
        return None

        def allow_migrate(self, db, app_label, model_name=None, **hints):
            """
            Migrate all 'knowledge' app models to the default database only.
            All other apps only migrate to 'default'.
            """
            if db == 'default':
                return True  # Migrate everything to default DB
            # Prevent migration of 'knowledge' app to knowledge DB
            if db == 'knowledge':
                return False
            return None