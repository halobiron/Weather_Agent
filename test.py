import asyncio
import aiohttp
import traceback
async def demo_unified_system():
    conversation_id = "demo_user_2025"
    
    async with aiohttp.ClientSession() as session:
        
        # BƯỚC 1: Hỏi thời tiết qua Weather API
        print("\nBƯỚC 1: User hỏi về thời tiết")
        print("-" * 70)
        
        question = "Thời tiết ở TP.HCM hôm nay thế nào? Xuất nội dung ra file Word chuyên nghiệp."
        weather_data = {
            "message": question,
            "conversation_id": conversation_id
        }
        
        print(f"User: {question}")
        print(f"Session ID: {conversation_id}")
        print(f"\nĐang gọi Weather Agent...")
        
        try:
            timeout = aiohttp.ClientTimeout(total=300, sock_connect=30, sock_read=180)
            async with session.post(
                "http://localhost:8000/ask",
                json=weather_data,
                timeout=timeout
            ) as response:
                if response.status == 200:
                    print(f"\nAssistant: ", end='', flush=True)
                    
                    full_response = ""
                    async for chunk in response.content.iter_any():
                        if chunk:
                            text = chunk.decode('utf-8', errors='ignore')
                            full_response += text
                            print(text, end='', flush=True)
                    
                    print(f"\n\nWeather Agent đã trả lời!")
                else:
                    print(f"Lỗi: {response.status}")
                    return
        except Exception as e:
            
            error_msg = f"Lỗi kết nối Weather API: {e}"
            print(error_msg)
            print(f"Chi tiết lỗi:\n{traceback.format_exc()}")
            return
        
        await asyncio.sleep(1)
        
        # BƯỚC 2: Xem lịch sử qua Weather API
        print("\n\nBƯỚC 2: Xem lịch sử qua Weather API (Chat History Management)")
        print("-" * 70)
        
        chat_id_to_edit = None
        chat_id_to_delete = None
        try:
            async with session.get(
                f"http://localhost:8000/chats/{conversation_id}"
            ) as response:
                if response.status == 200:
                    chats = await response.json()
                    print(f"Lấy lịch sử thành công!")
                    print(f"Tổng số messages: {len(chats)}")
                    
                    for i, chat in enumerate(chats, 1):
                        print(f"\n{i}. {chat['role'].upper()}:")
                        print(f"   Text: {chat['text'][:100]}...")
                        print(f"   Chat ID: {chat['chat_id']}")
                        print(f"   Thời gian: {chat['timestamp']}")
                        
                        # Lấy chat_id của user message đầu tiên để edit/delete
                        if chat['role'] == 'user' and not chat_id_to_edit:
                            chat_id_to_edit = chat['chat_id']
                            chat_id_to_delete = chat['chat_id']
        except Exception as e:
            print(f"Lỗi: {e}")
            print(f"Chi tiết:\n{traceback.format_exc()}")
        
        await asyncio.sleep(1)
        
        # BƯỚC 3: Sửa một chat message
        if chat_id_to_edit:
            print(f"\n\nBƯỚC 3: Sửa chat message")
            print("-" * 70)
            print(f"Chat ID cần sửa: {chat_id_to_edit}")
            
            update_data = {
                "text": "Thời tiết ở Hà Nội hôm nay ra sao?",
                "metadata": {"edited": True}
            }
            
            try:
                async with session.put(
                    f"http://localhost:8000/chats/{chat_id_to_edit}",
                    json=update_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"{result['message']}")
                    else:
                        error_text = await response.text()
                        print(f"Lỗi {response.status}: {error_text}")
            except Exception as e:      
                print(f"Lỗi: {e}")
                print(f"Chi tiết:\n{traceback.format_exc()}")
            
            await asyncio.sleep(1)
            
            # BƯỚC 4: Xóa một chat message
            print(f"\n\nBƯỚC 4: Xóa chat message")
            print("-" * 70)
            print(f"Chat ID cần xóa: {chat_id_to_delete}")
            
            try:
                async with session.delete(
                    f"http://localhost:8000/chats/{chat_id_to_delete}"
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"{result['message']}")
                    else:
                        error_text = await response.text()
                        print(f"Lỗi {response.status}: {error_text}")
            except Exception as e:
                print(f"Lỗi: {e}")
                print(f"Chi tiết:\n{traceback.format_exc()}")

            await asyncio.sleep(1)
            
            # BƯỚC 5: Kiểm tra lịch sử sau khi xóa
            print(f"\n\nBƯỚC 5: Kiểm tra lịch sử sau khi xóa")
            print("-" * 70)
            
            try:
                async with session.get(
                    f"http://localhost:8000/chats/{conversation_id}"
                ) as response:
                    if response.status == 200:
                        chats = await response.json()
                        print(f"Lấy lịch sử thành công!")
                        print(f"Tổng số messages sau xóa: {len(chats)}")
                        
                        for i, chat in enumerate(chats, 1):
                            print(f"\n{i}. {chat['role'].upper()}:")
                            print(f"   Text: {chat['text'][:100]}...")
                            print(f"   Chat ID: {chat['chat_id']}")
                    else:
                        error_text = await response.text()
                        print(f"Lỗi {response.status}: {error_text}")
            except Exception as e:
                print(f"Lỗi: {e}")
                print(f"Chi tiết:\n{traceback.format_exc()}")
        else:
            print("\nKhông tìm thấy chat message nào để edit/delete")

        print("DEMO HOÀN TẤT")

async def main():
    print("\nĐảm bảo đã chạy 'python main.py' trước!\n")
    
    await demo_unified_system()

if __name__ == "__main__":
    asyncio.run(main())
