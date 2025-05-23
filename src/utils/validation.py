def validate_input(name, author):
    errors = []
    if len(name) < 2:
        errors.append("Name must be at least 2 characters")
    if author and len(author) < 2:
        errors.append("Author name must be at least 2 characters")
    return errors