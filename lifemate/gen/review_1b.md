# Mẫu D để đọc tay

Mỗi mục: câu gốc → câu viết lại, nhãn gốc → nhãn mới. Đánh dấu [x] nếu hợp lý, ghi lý do nếu không.

## [ ] train_0030#d1 (B-vague)

- **Gốc:** Ơi, chuyển giúp tôi một triệu hai cho chủ nhà Phạm Hùng nhé.
- **Mới:** Ơi, chuyển giúp tôi một triệu hai nhé.
- **Nhãn gốc:** `[{"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_01", "beneficiary_id": "ben_01", "amount": 1200000}}]`
- **Nhãn mới:** `[{"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "banking.transfer", "params": ["beneficiary_id"]}}]`

## [ ] train_0045#d1 (B-vague)

- **Gốc:** Trợ lý ơi, chuyển giúp tôi cho anh Trần Văn Tuấn số tiền bằng hóa đơn nước tháng này nhé.
- **Mới:** Trợ lý ơi, chuyển giúp tôi số tiền bằng hóa đơn nước tháng này nhé.
- **Nhãn gốc:** `[{"name": "bill_payment.list_bills", "arguments": {}}, {"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_01", "beneficiary_id": "ben_03", "amount": 212000}}]`
- **Nhãn mới:** `[{"name": "bill_payment.list_bills", "arguments": {}}, {"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "banking.transfer", "params": ["beneficiary_id"]}}]`

## [ ] train_0177#d1 (B-vague)

- **Gốc:** Nhắn Zalo cho Minh giúp mình là đến rồi thì gọi tôi nha.
- **Mới:** Nhắn Zalo giúp mình là đến rồi thì gọi tôi nha.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.send_message", "arguments": {"chat_id": "chat_04", "content": "đến rồi thì gọi tôi"}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.send_message", "params": ["chat_id"]}}]`

## [ ] train_0682#d1 (B-vague)

- **Gốc:** Ừ, thế nhắn Zalo cho chị Ly bên trực kho một câu, bảo là cửa đấy khoá rồi nhé.
- **Mới:** Ừ, thế nhắn Zalo một câu, bảo là cửa đấy khoá rồi nhé.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.send_message", "arguments": {"chat_id": "chat_01", "content": "Cửa kho phía Bắc đã khóa rồi chị nhé."}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.send_message", "params": ["chat_id"]}}]`

## [ ] train_0230#d1 (B-vague)

- **Gốc:** Cho mình chuyển qua Nguyễn Thị Lan y số tiền nước tháng này nha, trừ tài khoản thanh toán, mà thiếu thì dùng tiết kiệm.
- **Mới:** Cho mình chuyển y số tiền nước tháng này nha, trừ tài khoản thanh toán, mà thiếu thì dùng tiết kiệm.
- **Nhãn gốc:** `[{"name": "bill_payment.list_bills", "arguments": {}}, {"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_02", "beneficiary_id": "ben_01", "amount": 215000}}]`
- **Nhãn mới:** `[{"name": "bill_payment.list_bills", "arguments": {}}, {"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "banking.transfer", "params": ["beneficiary_id"]}}]`

## [ ] train_0854#d1 (B-vague)

- **Gốc:** Gửi địa chỉ tiệm đó cho Lan qua Zalo giúp chị, dặn là bảy giờ tối chị sẽ qua đó nha.
- **Mới:** Gửi địa chỉ tiệm đó qua Zalo giúp chị, dặn là bảy giờ tối chị sẽ qua đó nha.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.send_message", "arguments": {"chat_id": "chat_06", "content": "Tiệm sửa xe Minh Phát ở 25 Phố Huế, Hai Bà Trưng. Bảy giờ tối mình sẽ qua đó."}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.send_message", "params": ["chat_id"]}}]`

## [ ] train_1260#d1 (B-vague)

- **Gốc:** Làm thủ tục chuyến mai luôn, rồi chuyển thằng Út ba trăm bằng tài khoản thanh toán.
- **Mới:** Làm thủ tục chuyến mai luôn, rồi chuyển ba trăm bằng tài khoản thanh toán.
- **Nhãn gốc:** `[{"name": "flights.check_in", "arguments": {"booking_id": "bk_205"}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_981", "beneficiary_id": "ben_637", "amount": 300000}}]`
- **Nhãn mới:** `[{"name": "flights.check_in", "arguments": {"booking_id": "bk_205"}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "banking.transfer", "params": ["beneficiary_id"]}}]`

## [ ] train_1564#d1 (B-vague)

- **Gốc:** Tiệm đó là Amber Jewelry, em xem giá nhẫn tròn hôm nay rồi chuyển tiền hai chỉ cho tiệm bằng tài khoản thanh toán nha.
- **Mới:** Em xem giá nhẫn tròn hôm nay rồi chuyển tiền hai chỉ cho tiệm vàng bằng tài khoản thanh toán nha.
- **Nhãn gốc:** `[{"name": "gold_price.get_price", "arguments": {"type": "ring"}}, {"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_749", "beneficiary_id": "ben_6021", "amount": 23220000}}]`
- **Nhãn mới:** `[{"name": "gold_price.get_price", "arguments": {"type": "ring"}}, {"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "banking.transfer", "params": ["beneficiary_id"]}}]`

## [ ] train_0468#d1 (C)

- **Gốc:** Có tin gì mới về năng lượng mặt trời không, tìm cho tôi bài mới nhất, rồi tám giờ tối nay nhắc tôi đọc bài đấy nhé.
- **Mới:** Có tin gì mới về năng lượng mặt trời không, tìm cho tôi bài mới nhất, rồi nhắc tôi đọc bài đấy nhé.
- **Nhãn gốc:** `[{"name": "news.search", "arguments": {"query": "năng lượng mặt trời"}}, {"name": "reminders.create", "arguments": {"content": "Đọc bài Mái nhà dùng pin mặt trời", "time": "2026-09-25T20:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "news.search", "arguments": {"query": "năng lượng mặt trời"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0829#d1 (C)

- **Gốc:** Ừ, cái gói xem phim Stream Plus ấy tôi ít xem lắm, hủy đi. Rồi ghi vào lịch cái ngày nó hết hạn giúp tôi, để tám giờ sáng hôm đó cho dễ thấy nhé.
- **Mới:** Ừ, cái gói xem phim Stream Plus ấy tôi ít xem lắm, hủy đi. Rồi ghi vào lịch cái ngày nó hết hạn giúp tôi nhé.
- **Nhãn gốc:** `[{"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_05"}}, {"name": "calendar.create_event", "arguments": {"title": "Gói Stream Plus hết hạn", "start": "2026-10-31T08:00:00+07:00", "end": "2026-10-31T09:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_05"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.create_event", "params": ["start"]}}]`

## [ ] train_1647#d1 (C)

- **Gốc:** Ghi giùm anh bốn mươi lăm phút học tiếng Hàn tối ni, với nhắc bảy giờ sáng mai ôn từ vựng gặp client nghe.
- **Mới:** Ghi giùm anh bốn mươi lăm phút học tiếng Hàn tối ni, với nhắc ôn từ vựng gặp client nghe.
- **Nhãn gốc:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "learning.log_progress", "arguments": {"course_id": "course_6206", "minutes": 45}}, {"name": "reminders.create", "arguments": {"content": "Ôn từ vựng gặp client", "time": "2026-11-24T07:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "learning.log_progress", "arguments": {"course_id": "course_6206", "minutes": 45}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0785#d1 (C)

- **Gốc:** Ừ, thêm hai việc đấy vào danh sách việc của em, giữ đúng hạn trong nhóm. Rồi qua hạn sớm nhất một ngày thì đặt lịch chín giờ sáng để kiểm tra tiến độ chung nhé.
- **Mới:** Ừ, thêm hai việc đấy vào danh sách việc của em, giữ đúng hạn trong nhóm. Rồi qua hạn sớm nhất một ngày thì đặt lịch để kiểm tra tiến độ chung nhé.
- **Nhãn gốc:** `[{"name": "tasks.add", "arguments": {"title": "Chốt ảnh sản phẩm", "due": "2026-10-10T17:00:00+07:00"}}, {"name": "tasks.add", "arguments": {"title": "Soát thông cáo báo chí", "due": "2026-10-12T17:00:00+07:00"}}, {"name": "calendar.create_event", "arguments": {"title": "Kiểm tra tiến độ nhóm ra mắt sản phẩm", "start": "2026-10-11T09:00:00+07:00", "end": "2026-10-11T10:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "tasks.add", "arguments": {"title": "Chốt ảnh sản phẩm", "due": "2026-10-10T17:00:00+07:00"}}, {"name": "tasks.add", "arguments": {"title": "Soát thông cáo báo chí", "due": "2026-10-12T17:00:00+07:00"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.create_event", "params": ["start"]}}]`

## [ ] train_0294#d1 (C)

- **Gốc:** Em tắt đèn phòng ngủ hộ chị... ấy quên, thôi đừng tắt, cứ để sáng vậy đi. Bật điều hoà phòng ngủ 24 độ với 7 giờ sáng mai nhắc chị đóng tiền điện nha.
- **Mới:** Em tắt đèn phòng ngủ hộ chị... ấy quên, thôi đừng tắt, cứ để sáng vậy đi. Bật điều hoà phòng ngủ 24 độ với nhắc chị đóng tiền điện nha.
- **Nhãn gốc:** `[{"name": "smart_home.get_status", "arguments": {}}, {"name": "smart_home.climate_set", "arguments": {"device_id": "ac_bedroom", "mode": "cool", "temperature": 24}}, {"name": "reminders.create", "arguments": {"content": "đóng tiền điện", "time": "2026-11-21T07:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "smart_home.get_status", "arguments": {}}, {"name": "smart_home.climate_set", "arguments": {"device_id": "ac_bedroom", "mode": "cool", "temperature": 24}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0862#d1 (C)

- **Gốc:** Mai mà trời không mưa thì em lên lịch chạy bộ cho chị lúc sáu giờ sáng nha.
- **Mới:** Mai mà trời không mưa thì em lên lịch chạy bộ cho chị nha.
- **Nhãn gốc:** `[{"name": "weather.get_forecast", "arguments": {"date": "2026-09-21"}}, {"name": "calendar.create_event", "arguments": {"title": "Chạy bộ", "start": "2026-09-21T06:00:00+07:00", "end": "2026-09-21T07:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "weather.get_forecast", "arguments": {"date": "2026-09-21"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.create_event", "params": ["start"]}}]`

## [ ] train_1638#d1 (C)

- **Gốc:** Con kiếm giùm cô công thức canh chua cá lóc, với nhắc cô sáu giờ sáng mai đi chợ mua cá lóc nha.
- **Mới:** Con kiếm giùm cô công thức canh chua cá lóc, với nhắc cô đi chợ mua cá lóc nha.
- **Nhãn gốc:** `[{"name": "reminders.create", "arguments": {"content": "Đi chợ mua cá lóc", "time": "2026-11-17T06:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0831#d1 (C)

- **Gốc:** Trả bằng tài khoản ngân hàng nhé. Xong nhắc anh đối soát hóa đơn đó lúc chín giờ sáng, trước hạn khiếu nại một ngày.
- **Mới:** Trả bằng tài khoản ngân hàng nhé. Xong nhắc anh đối soát hóa đơn đó trước hạn khiếu nại một ngày.
- **Nhãn gốc:** `[{"name": "bill_payment.pay", "arguments": {"bill_id": "bill_03", "source": "bank"}}, {"name": "reminders.create", "arguments": {"content": "Đối soát hóa đơn điện văn phòng", "time": "2026-10-11T09:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "bill_payment.pay", "arguments": {"bill_id": "bill_03", "source": "bank"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0485#d1 (C)

- **Gốc:** Ừ, vậy em đặt nhắc chị sáng hôm đó đúng bảy giờ uống viên sắt nhé.
- **Mới:** Ừ, vậy em đặt nhắc chị uống viên sắt nhé.
- **Nhãn gốc:** `[{"name": "reminders.create", "arguments": {"content": "Uống viên sắt", "time": "2026-09-27T07:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0433#d1 (C)

- **Gốc:** Hà Nội giờ mà đang mưa thì mười giờ nhắc chị cầm ô theo nhé.
- **Mới:** Hà Nội giờ mà đang mưa thì nhắc chị cầm ô theo nhé.
- **Nhãn gốc:** `[{"name": "weather.get_current", "arguments": {}}, {"name": "reminders.create", "arguments": {"content": "Cầm ô theo", "time": "2026-09-24T10:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "weather.get_current", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0411#d1 (C)

- **Gốc:** Vàng SJC bán ra hôm nay trên 122 triệu thì nhắc tôi chín giờ sáng mai bán vàng, chưa tới thì chuyển Trần Văn Tuấn hai triệu từ tài khoản thanh toán, góp mua vàng.
- **Mới:** Vàng SJC bán ra hôm nay trên 122 triệu thì nhắc tôi bán vàng, chưa tới thì chuyển Trần Văn Tuấn hai triệu từ tài khoản thanh toán, góp mua vàng.
- **Nhãn gốc:** `[{"name": "gold_price.get_price", "arguments": {"type": "sjc"}}, {"name": "reminders.create", "arguments": {"content": "đi bán vàng", "time": "2026-11-06T09:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "gold_price.get_price", "arguments": {"type": "sjc"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1138#d1 (C)

- **Gốc:** Gói năm mươi chín nghìn nào trừ tiền sớm hơn thì huỷ đi. Tám giờ sáng hôm trước ngày trừ tiền phòng gym, nhắc tôi gọi thằng Tuấn.
- **Mới:** Gói năm mươi chín nghìn nào trừ tiền sớm hơn thì huỷ đi. Hôm trước ngày trừ tiền phòng gym, nhắc tôi gọi thằng Tuấn.
- **Nhãn gốc:** `[{"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_3573"}}, {"name": "reminders.create", "arguments": {"content": "Gọi thằng Tuấn", "time": "2026-11-14T08:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_3573"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1315#d1 (C)

- **Gốc:** Cái bật đèn phòng khách bỏ đi hỉ, tốn điện lắm. Với sáng mai sáu rưỡi nhắc em gọi cho mạ nghe.
- **Mới:** Cái bật đèn phòng khách bỏ đi hỉ, tốn điện lắm. Với nhắc em gọi cho mạ nghe.
- **Nhãn gốc:** `[{"name": "home_automation.delete_rule", "arguments": {"rule_id": "rule_2403"}}, {"name": "reminders.create", "arguments": {"content": "Gọi mạ", "time": "2026-10-17T06:30:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "home_automation.delete_rule", "arguments": {"rule_id": "rule_2403"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0537#d1 (C)

- **Gốc:** Kiếm giùm anh bài mới nhất về điện mặt trời coi, rồi tám giờ tối nay nhắc anh đọc đúng bài đó nha.
- **Mới:** Kiếm giùm anh bài mới nhất về điện mặt trời coi, rồi nhắc anh đọc đúng bài đó nha.
- **Nhãn gốc:** `[{"name": "news.search", "arguments": {"query": "điện mặt trời"}}, {"name": "reminders.create", "arguments": {"content": "Đọc bài Mái nhà dùng pin mặt trời", "time": "2026-09-25T20:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "news.search", "arguments": {"query": "điện mặt trời"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0973#d1 (C)

- **Gốc:** Chiếc điện cho tôi, tôi chạy giao mấy mối cho kịp. Giữ thêm chiếc thường cho Tí đạp theo, rồi nhắc tôi tám giờ đem trả xe nha.
- **Mới:** Chiếc điện cho tôi, tôi chạy giao mấy mối cho kịp. Giữ thêm chiếc thường cho Tí đạp theo, rồi nhắc tôi đem trả xe nha.
- **Nhãn gốc:** `[{"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_7299"}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_764"}}, {"name": "reminders.create", "arguments": {"content": "Đem trả xe đạp", "time": "2026-11-14T08:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_7299"}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_764"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1063#d1 (C)

- **Gốc:** Giờ cao điểm điện mắc lắm con, máy giặt với máy rửa chén cái nào còn chạy thì tắt, rồi đặt lời nhắc mười giờ tối cô mở lại nha.
- **Mới:** Giờ cao điểm điện mắc lắm con, máy giặt với máy rửa chén cái nào còn chạy thì tắt, rồi đặt lời nhắc cô mở lại nha.
- **Nhãn gốc:** `[{"name": "appliances.list", "arguments": {}}, {"name": "appliances.stop", "arguments": {"appliance_id": "appl_3371"}}, {"name": "reminders.create", "arguments": {"content": "Mở lại máy giặt", "time": "2026-10-12T22:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "appliances.list", "arguments": {}}, {"name": "appliances.stop", "arguments": {"appliance_id": "appl_3371"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`
