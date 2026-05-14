import sys

def parser(path: str) -> None:
    try:
        with open(path, 'r') as l:
            data = l.read()
            print(data)
    except FileNotFoundError as e:
        print(f"Error while trying to read {path}: {e}")
    
def params(data):
    try:
        

def main():
    path = sys.argv[1]
    parser(path)

if __name__ == "__main__":
    main()
