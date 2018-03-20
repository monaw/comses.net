class DumpRestoreRouter:
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'dump_restore':
            return False
        return None


class DefaultRouter:
    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True