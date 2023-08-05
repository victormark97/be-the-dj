from django.core.exceptions import ValidationError, ImproperlyConfigured


def sanitize_fields(data, model):
    sanitized_data = {}
    try:
        for field in model._meta.get_fields():
            if not field.many_to_many and not field.one_to_many:
                if field.name in data:
                    sanitized_data[field.name] = data[field.name]
                elif field.has_default() or field.null or field.blank:
                    sanitized_data[field.name] = field.get_default()
    except ImproperlyConfigured as e:
        raise ValidationError({"error": f"Missing required field for {model.__name__}"})
    
    return sanitized_data


def create_model_instance(data, model):
    """
    Generic function to create a model instance.
    Ignores extra fields and fills in default values for missing non-required fields.
    """
    data = sanitize_fields(data, model)

    try:
        instance = model.objects.create(**data)
        return instance
    except ValidationError as e:
        raise ValidationError({"error": str(e)})
    except Exception as e:
        raise ValidationError({"error": "An error occurred during instance creation: " + str(e)})
    

def update_or_create_model_instance(data, model):
    """
    Generic function to create a model instance.
    Ignores extra fields and fills in default values for missing non-required fields.
    """
    data = sanitize_fields(data, model)

    try:
        instance = model.objects.update_or_create(**data)
        return instance
    except ValidationError as e:
        raise ValidationError({"error": str(e)})
    except Exception as e:
        raise ValidationError({"error": "An error occurred during instance creation: " + str(e)})