from app.agent import validate_user_input

question = 'Calculate __import__("os").getcwd()'
error = validate_user_input(question)

print("ERROR:", error)
print("WOULD EXIT:", bool(error))
