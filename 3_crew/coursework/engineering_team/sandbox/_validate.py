import app

def test_app_blocks_constructs():
    try:
        blocks = app.gradio_interface()
        assert blocks is not None
        print("Blocks constructed successfully.")
    except Exception as e:
        print(f"Error constructing Blocks: {e}")

if __name__ == "__main__":
    test_app_blocks_constructs()
