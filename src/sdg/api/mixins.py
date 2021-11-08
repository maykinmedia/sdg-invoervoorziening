class MultipleSerializerMixin:
    serializer_classes = {}

    def get_serializer_class(self):
        if self.action not in self.serializer_classes:
            return super().get_serializer_class()

        return self.serializer_classes[self.action]
