# Mẫu D để đọc tay

Mỗi mục: câu gốc → câu viết lại, nhãn gốc → nhãn mới. Đánh dấu [x] nếu hợp lý, ghi lý do nếu không.

## [ ] train_0950#d1 (B-specific)

- **Gốc:** Con ơi, sáng ni cô muốn đạp xe dọc biển, giữ giùm cô một chiếc ở trạm Biển Đông nghe.
- **Mới:** Con ơi, sáng ni cô muốn đạp xe dọc biển, giữ giùm cô chiếc xe đạp thường 104 ở trạm Biển Đông nghe.
- **Nhãn gốc:** `[{"name": "bike_rental.find_bikes", "arguments": {"near": "Biển Đông"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "bike_rental.reserve", "params": ["bike_id"]}}]`
- **Nhãn mới:** `[{"name": "bike_rental.find_bikes", "arguments": {"near": "Biển Đông"}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_724"}}]`

## [ ] train_0955#d1 (B-specific)

- **Gốc:** Ờ tắt hết đèn quạt phòng ngủ, à nhầm, phòng làm việc, rồi đánh dấu xong việc gửi báo cáo nhé.
- **Mới:** Ờ tắt hết đèn quạt phòng ngủ, à nhầm, phòng làm việc, rồi đánh dấu xong việc gửi báo cáo tuần cho sếp Dũng nhé.
- **Nhãn gốc:** `[{"name": "smart_home.get_status", "arguments": {"room": "phòng làm việc"}}, {"name": "smart_home.light_set", "arguments": {"device_id": "light_office", "power": "off"}}, {"name": "smart_home.light_set", "arguments": {"device_id": "light_desk", "power": "off"}}, {"name": "smart_home.fan_set", "arguments": {"device_id": "fan_office", "power": "off"}}, {"name": "tasks.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "tasks.complete", "params": ["task_id"]}}]`
- **Nhãn mới:** `[{"name": "smart_home.get_status", "arguments": {"room": "phòng làm việc"}}, {"name": "smart_home.light_set", "arguments": {"device_id": "light_office", "power": "off"}}, {"name": "smart_home.light_set", "arguments": {"device_id": "light_desk", "power": "off"}}, {"name": "smart_home.fan_set", "arguments": {"device_id": "fan_office", "power": "off"}}, {"name": "tasks.list", "arguments": {}}, {"name": "tasks.complete", "arguments": {"task_id": "task_517"}}]`

## [ ] train_1303#d1 (B-specific)

- **Gốc:** Con xoá lẹ giùm cô cái nhắc đi chợ nghe.
- **Mới:** Con xoá lẹ giùm cô cái nhắc đi chợ Cồn mua đồ đám giỗ nghe.
- **Nhãn gốc:** `[{"name": "reminders.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.delete", "params": ["reminder_id"]}}]`
- **Nhãn mới:** `[{"name": "reminders.list", "arguments": {}}, {"name": "reminders.delete", "arguments": {"reminder_id": "rem_1307"}}]`

## [ ] train_1109#d1 (B-specific)

- **Gốc:** Lan chuyển tiền học cho Bống rồi đấy, cái nhắc đóng tiền học tuần sau ấy em đánh dấu xong hộ anh nhé.
- **Mới:** Lan chuyển tiền học cho Bống rồi đấy, cái nhắc đóng tiền học bơi ấy em đánh dấu xong hộ anh nhé.
- **Nhãn gốc:** `[{"name": "reminders.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.complete", "params": ["reminder_id"]}}]`
- **Nhãn mới:** `[{"name": "reminders.list", "arguments": {}}, {"name": "reminders.complete", "arguments": {"reminder_id": "rem_352"}}]`

## [ ] train_0974#d1 (B-specific)

- **Gốc:** Nhắn vợ là anh nhớ rồi... à thôi khỏi. Coi cái bài sửa đường gần nhà anh, lưu lại giùm.
- **Mới:** Nhắn vợ là anh nhớ rồi... à thôi khỏi. Coi cái bài sửa đường Nguyễn Oanh gần nhà anh, lưu lại giùm.
- **Nhãn gốc:** `[{"name": "news.search", "arguments": {"query": "sửa đường"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "news.save", "params": ["article_id"]}}]`
- **Nhãn mới:** `[{"name": "news.search", "arguments": {"query": "sửa đường"}}, {"name": "news.save", "arguments": {"article_id": "art_617"}}]`

## [ ] train_1010#d1 (B-specific)

- **Gốc:** Mấy gói coi phim trừ tiền tuần sau á, hai cái thì dư, hủy dùm anh một cái thôi nha.
- **Mới:** Mấy gói coi phim trừ tiền tuần sau á, hai cái thì dư, hủy dùm anh cái Vitech Play thôi nha.
- **Nhãn gốc:** `[{"name": "subscriptions.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "subscriptions.cancel", "params": ["subscription_id"]}}]`
- **Nhãn mới:** `[{"name": "subscriptions.list", "arguments": {}}, {"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_3092"}}]`

## [ ] train_1449#d1 (B-specific)

- **Gốc:** Lúc anh rời nhà đi đón Kevin Park, có cái máy hẹn chạy sau giờ đó, em dừng giùm anh nghe.
- **Mới:** Lúc anh rời nhà đi đón Kevin Park, có cái máy rửa bát hẹn chạy sau giờ đó, em dừng giùm anh nghe.
- **Nhãn gốc:** `[{"name": "appliances.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "appliances.stop", "params": ["appliance_id"]}}]`
- **Nhãn mới:** `[{"name": "appliances.list", "arguments": {}}, {"name": "appliances.stop", "arguments": {"appliance_id": "appl_977"}}]`

## [ ] train_1500#d1 (B-vague)

- **Gốc:** Thêm lịch Sếp Kim qua lấy hồ sơ ở nhà mình lúc ba giờ chiều nay, rồi hẹn máy giặt chạy đồ dày đúng giờ đó luôn.
- **Mới:** Thêm lịch Sếp Kim qua lấy hồ sơ ở nhà mình lúc ba giờ chiều nay, rồi hẹn máy chạy đúng giờ đó luôn.
- **Nhãn gốc:** `[{"name": "calendar.create_event", "arguments": {"title": "Sếp Kim qua lấy hồ sơ", "start": "2026-11-05T15:00:00+07:00", "location": "Chung cư An Thảo, Thảo Điền, TP. Thủ Đức"}}, {"name": "appliances.list", "arguments": {}}, {"name": "appliances.start_cycle", "arguments": {"appliance_id": "appl_426", "cycle": "heavy", "delay_minutes": 85}}]`
- **Nhãn mới:** `[{"name": "calendar.create_event", "arguments": {"title": "Sếp Kim qua lấy hồ sơ", "start": "2026-11-05T15:00:00+07:00", "location": "Chung cư An Thảo, Thảo Điền, TP. Thủ Đức"}}, {"name": "appliances.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "appliances.start_cycle", "params": ["appliance_id"]}}]`

## [ ] train_0523#d1 (B-vague)

- **Gốc:** Trả tiền nước quý ba trước đi, lấy tiền trong ví ấy.
- **Mới:** Trả cái đó trước đi, lấy tiền trong ví ấy.
- **Nhãn gốc:** `[{"name": "bill_payment.list_bills", "arguments": {}}, {"name": "bill_payment.pay", "arguments": {"bill_id": "bill_05", "source": "ewallet"}}]`
- **Nhãn mới:** `[{"name": "bill_payment.list_bills", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "bill_payment.pay", "params": ["bill_id"]}}]`

## [ ] train_0919#d1 (B-vague)

- **Gốc:** Ờ… gọi thằng Bi coi, ờ, gọi video Zalo nha, anh coi mặt nó cái.
- **Mới:** Ờ… gọi nó coi, ờ, gọi video Zalo nha, anh coi mặt nó cái.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.call", "arguments": {"chat_id": "chat_340", "video": true}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.call", "params": ["chat_id"]}}]`

## [ ] train_1197#d1 (B-vague)

- **Gốc:** Ơ... gửi vị trí của tớ vào nhóm Zalo phòng hai không bốn nha, đường về kí túc tối quá.
- **Mới:** Ơ... gửi vị trí của tớ vào nhóm Zalo nha, đường về tối quá.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.send_location", "arguments": {"chat_id": "chat_1015"}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.send_location", "params": ["chat_id"]}}]`

## [ ] train_0743#d1 (B-vague)

- **Gốc:** Giữ giùm anh chiếc xe đạp chở hàng ở trạm Chợ Hôm nha, chút nữa anh ghé lấy.
- **Mới:** Giữ giùm anh một chiếc xe đạp ở trạm Chợ Hôm nha, chút nữa anh ghé lấy.
- **Nhãn gốc:** `[{"name": "bike_rental.find_bikes", "arguments": {"near": "Chợ Hôm"}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_07"}}]`
- **Nhãn mới:** `[{"name": "bike_rental.find_bikes", "arguments": {"near": "Chợ Hôm"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "bike_rental.reserve", "params": ["bike_id"]}}]`

## [ ] train_1365#d1 (C)

- **Gốc:** Hẹn giao lại cái ốp lưng điện thoại vô tám giờ sáng mai giùm tôi nha, bữa nay chờ hoài hổng thấy ai tới.
- **Mới:** Hẹn giao lại cái ốp lưng điện thoại giùm tôi nha, bữa nay chờ hoài hổng thấy ai tới.
- **Nhãn gốc:** `[{"name": "package_tracking.track", "arguments": {}}, {"name": "package_tracking.reschedule_delivery", "arguments": {"tracking_id": "MDXVN236907673", "time": "2026-11-14T08:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "package_tracking.track", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "package_tracking.reschedule_delivery", "params": ["time"]}}]`

## [ ] train_0875#d1 (C)

- **Gốc:** Anh không xem nữa đâu, huỷ cái gói Xem Phim Plus đi em. Rồi soạn sẵn cái thư nháp gửi family a còng example chấm test, báo cả nhà là từ tháng sau mình thôi không dùng gói đó nữa.
- **Mới:** Anh không xem nữa đâu, huỷ cái gói Xem Phim Plus đi em. Rồi soạn sẵn cái thư nháp, báo cả nhà là từ tháng sau mình thôi không dùng gói đó nữa.
- **Nhãn gốc:** `[{"name": "subscriptions.list", "arguments": {}}, {"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_05"}}, {"name": "email.create_draft", "arguments": {"to": ["family@example.test"], "subject": "Dừng gói Xem Phim Plus", "body": "Cả nhà ơi, từ tháng sau nhà mình không dùng gói Xem Phim Plus nữa nhé."}}]`
- **Nhãn mới:** `[{"name": "subscriptions.list", "arguments": {}}, {"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_05"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "email.create_draft", "params": ["to"]}}]`

## [ ] train_0827#d1 (C)

- **Gốc:** Kho sân sau cứ để đấy, chiều anh còn ra lấy đồ. Em khóa cái kho dụng cụ lại giúp anh, khóa xong thì cài luôn cho anh cứ bảy rưỡi tối là đèn sân tự bật nhé.
- **Mới:** Kho sân sau cứ để đấy, chiều anh còn ra lấy đồ. Em khóa cái kho dụng cụ lại giúp anh, khóa xong thì cài luôn cho anh đèn sân tự bật nhé.
- **Nhãn gốc:** `[{"name": "door_lock.set_lock", "arguments": {"lock_id": "lock_06", "locked": true}}, {"name": "smart_home.get_status", "arguments": {}}, {"name": "home_automation.create_rule", "arguments": {"device_id": "light_yard", "action": "on", "time": "19:30", "title": "Bật đèn sân lúc 19:30"}}]`
- **Nhãn mới:** `[{"name": "door_lock.set_lock", "arguments": {"lock_id": "lock_06", "locked": true}}, {"name": "smart_home.get_status", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "home_automation.create_rule", "params": ["time"]}}]`

## [ ] train_1450#d1 (C)

- **Gốc:** Hôm qua chưa được nửa mục tiêu thì hạ xuống sáu nghìn bước nghe. À, nạp năm chục nghìn tiền điện thoại cho Lucas luôn.
- **Mới:** Hôm qua chưa được nửa mục tiêu thì hạ xuống sáu nghìn bước nghe. À, nạp tiền điện thoại cho Lucas luôn.
- **Nhãn gốc:** `[{"name": "fitness.set_goal", "arguments": {"steps": 6000}}, {"name": "contacts.search", "arguments": {"query": "Lucas"}}, {"name": "ewallet.topup_mobile", "arguments": {"phone": "09336281608", "amount": 50000}}]`
- **Nhãn mới:** `[{"name": "fitness.set_goal", "arguments": {"steps": 6000}}, {"name": "contacts.search", "arguments": {"query": "Lucas"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "ewallet.topup_mobile", "params": ["amount"]}}]`

## [ ] train_1364#d1 (C)

- **Gốc:** Anh bơi xong rồi, em ghi buổi tập đúng như Kevin Walsh dặn nhé, với đặt báo thức năm giờ rưỡi sáng mai giúp anh.
- **Mới:** Anh bơi xong rồi, em ghi buổi tập đúng như Kevin Walsh dặn nhé, với đặt báo thức sáng mai giúp anh.
- **Nhãn gốc:** `[{"name": "fitness.log_workout", "arguments": {"type": "swimming", "minutes": 45}}, {"name": "alarm.create", "arguments": {"time": "2026-12-18T05:30:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "fitness.log_workout", "arguments": {"type": "swimming", "minutes": 45}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "alarm.create", "params": ["time"]}}]`

## [ ] train_0828#d1 (C)

- **Gốc:** Ơ bạn ơi, thứ sáu này hẹn bưu điện qua số 18 phố Trúc Bạch lấy gói hàng giúp mình nha. Với cả sáu giờ chiều hôm trước nhắc mình in cái nhãn dán nữa.
- **Mới:** Ơ bạn ơi, thứ sáu này hẹn bưu điện qua số 18 phố Trúc Bạch lấy gói hàng giúp mình nha. Với cả nhắc mình in cái nhãn dán nữa.
- **Nhãn gốc:** `[{"name": "package_tracking.schedule_pickup", "arguments": {"address": "18 phố Trúc Bạch", "date": "2026-10-09"}}, {"name": "reminders.create", "arguments": {"content": "In nhãn dán gói hàng", "time": "2026-10-08T18:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "package_tracking.schedule_pickup", "arguments": {"address": "18 phố Trúc Bạch", "date": "2026-10-09"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1428#d1 (C)

- **Gốc:** Lấy số tiền Greenhaven Foods mới chuyển, gửi tiết kiệm sáu tháng từ tài khoản vựa giùm tôi.
- **Mới:** Lấy số tiền Greenhaven Foods mới chuyển, gửi tiết kiệm từ tài khoản vựa giùm tôi.
- **Nhãn gốc:** `[{"name": "banking.open_savings", "arguments": {"from_account_id": "acc_205", "amount": 18500000, "term_months": 6}}]`
- **Nhãn mới:** `[{"name": "sys.ask_missing_info", "arguments": {"tool_name": "banking.open_savings", "params": ["term_months"]}}]`

## [ ] train_1279#d1 (C)

- **Gốc:** Tờ đầu đài Đà Nẵng, tờ sau Đồng Nai. Trúng tờ nào thì chuyển ví anh Long hai trăm nha.
- **Mới:** Tờ đầu đài Đà Nẵng, tờ sau Đồng Nai. Trúng tờ nào thì chuyển ví anh Long nha.
- **Nhãn gốc:** `[{"name": "lottery.check_ticket", "arguments": {"province": "Đà Nẵng", "date": "2026-10-10", "number": "512327"}}, {"name": "lottery.check_ticket", "arguments": {"province": "Đồng Nai", "date": "2026-10-10", "number": "834520"}}, {"name": "contacts.search", "arguments": {"query": "Anh Long"}}, {"name": "ewallet.transfer", "arguments": {"contact_id": "c_6885", "amount": 200000}}]`
- **Nhãn mới:** `[{"name": "lottery.check_ticket", "arguments": {"province": "Đà Nẵng", "date": "2026-10-10", "number": "512327"}}, {"name": "lottery.check_ticket", "arguments": {"province": "Đồng Nai", "date": "2026-10-10", "number": "834520"}}, {"name": "contacts.search", "arguments": {"query": "Anh Long"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "ewallet.transfer", "params": ["amount"]}}]`

## [ ] train_1245#d1 (C)

- **Gốc:** Đơn sách Nhà giả kim mai giao á, dời sang chín rưỡi sáng thứ hai giúp tớ nha.
- **Mới:** Đơn sách Nhà giả kim mai giao á, dời lại giúp tớ nha.
- **Nhãn gốc:** `[{"name": "package_tracking.track", "arguments": {}}, {"name": "package_tracking.reschedule_delivery", "arguments": {"tracking_id": "JV677561954", "time": "2026-11-09T09:30:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "package_tracking.track", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "package_tracking.reschedule_delivery", "params": ["time"]}}]`

## [ ] train_0448#d1 (C)

- **Gốc:** Hủy giúp tôi cái gói Đọc Sách Pro nhé, rồi soạn sẵn một thư nháp gửi family a còng example chấm test, báo là tháng sau nhà mình không gia hạn nữa. Cứ để nháp đấy, tôi xem lại rồi mới gửi.
- **Mới:** Hủy giúp tôi cái gói Đọc Sách Pro nhé, rồi soạn sẵn một thư nháp báo là tháng sau nhà mình không gia hạn nữa. Cứ để nháp đấy, tôi xem lại rồi mới gửi.
- **Nhãn gốc:** `[{"name": "subscriptions.list", "arguments": {}}, {"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_04"}}, {"name": "email.create_draft", "arguments": {"to": ["family@example.test"], "subject": "Dừng gói Đọc Sách Pro", "body": "Từ tháng sau nhà mình không gia hạn gói Đọc Sách Pro nữa."}}]`
- **Nhãn mới:** `[{"name": "subscriptions.list", "arguments": {}}, {"name": "subscriptions.cancel", "arguments": {"subscription_id": "sub_04"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "email.create_draft", "params": ["to"]}}]`

## [ ] train_0012#d1 (C)

- **Gốc:** Bạn ơi, chuyển cho chủ nhà Phạm Hùng hai triệu tám và nạp giúp sếp Dũng hai trăm nghìn nhé.
- **Mới:** Bạn ơi, chuyển cho chủ nhà Phạm Hùng hai triệu tám và nạp tiền điện thoại giúp sếp Dũng nhé.
- **Nhãn gốc:** `[{"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_01", "beneficiary_id": "ben_03", "amount": 2800000}}, {"name": "contacts.search", "arguments": {"query": "Sếp Dũng"}}, {"name": "ewallet.topup_mobile", "arguments": {"phone": "09698429175", "amount": 200000}}]`
- **Nhãn mới:** `[{"name": "banking.get_balance", "arguments": {}}, {"name": "banking.list_beneficiaries", "arguments": {}}, {"name": "banking.transfer", "arguments": {"from_account_id": "acc_01", "beneficiary_id": "ben_03", "amount": 2800000}}, {"name": "contacts.search", "arguments": {"query": "Sếp Dũng"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "ewallet.topup_mobile", "params": ["amount"]}}]`
