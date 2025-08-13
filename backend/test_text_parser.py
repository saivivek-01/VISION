from utils.text_parser import parse_text_file

if __name__ == "__main__":
    try:
        test_path = "/Users/villainvivek/VISION/backend/test_docs/sample.txt"  # Replace with your actual test file path
        output = parse_text_file(test_path)
        print("\n✅ Narration Output:\n")
        print(output)
    except Exception as e:
        print("❌ Error during parsing:", str(e))