from extensions import Flask

# For the modules of the system (Blueprint contains the module functions) 

def register_blueprints(app: Flask) -> None:
    
    from .user.user import userBp
    from .userProfile.userProfile import userProfileBp

    
    blueprints = [
        userBp,
        userProfileBp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)