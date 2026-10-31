# Mẫu D để đọc tay

Mỗi mục: câu gốc → câu viết lại, nhãn gốc → nhãn mới. Đánh dấu [x] nếu hợp lý, ghi lý do nếu không.

## [ ] train_0698#d1 (C)

- **Gốc:** Giữ cho tôi chiếc xe đạp chở hàng ở trạm Chợ Hôm, xem luôn đường từ trạm đó tới điểm thu gom tái chế Lò Đúc, rồi tạo lịch Bàn giao vật liệu tái chế lúc mười giờ sáng thứ tư tuần sau.
- **Mới:** Giữ cho tôi chiếc xe đạp chở hàng ở trạm Chợ Hôm, xem luôn đường từ trạm đó tới điểm thu gom tái chế Lò Đúc, rồi tạo lịch Bàn giao vật liệu tái chế giúp tôi.
- **Nhãn gốc:** `[{"name": "bike_rental.find_bikes", "arguments": {}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_05"}}, {"name": "maps.get_route", "arguments": {"origin": "Trạm xe đạp Chợ Hôm", "destination": "Điểm thu gom tái chế Lò Đúc"}}, {"name": "calendar.create_event", "arguments": {"title": "Bàn giao vật liệu tái chế", "start": "2026-10-07T10:00:00+07:00", "end": "2026-10-07T11:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "bike_rental.find_bikes", "arguments": {}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_05"}}, {"name": "maps.get_route", "arguments": {"origin": "Trạm xe đạp Chợ Hôm", "destination": "Điểm thu gom tái chế Lò Đúc"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.create_event", "params": ["start"]}}]`

## [ ] train_0500#d1 (C)

- **Gốc:** Chuyển cho Hòa một trăm hai mươi nghìn qua ví giúp anh cái.
- **Mới:** Chuyển cho Hòa qua ví giúp anh cái.
- **Nhãn gốc:** `[{"name": "contacts.search", "arguments": {"query": "Hòa"}}, {"name": "ewallet.transfer", "arguments": {"contact_id": "c_05", "amount": 120000}}]`
- **Nhãn mới:** `[{"name": "contacts.search", "arguments": {"query": "Hòa"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "ewallet.transfer", "params": ["amount"]}}]`

## [ ] train_1034#d1 (B-vague)

- **Gốc:** Tắt lẹ cái máy lọc không khí ngoài phòng khách coi, anh ra xe chạy rồi.
- **Mới:** Tắt lẹ cái máy coi, anh ra xe chạy rồi.
- **Nhãn gốc:** `[{"name": "appliances.list", "arguments": {}}, {"name": "appliances.stop", "arguments": {"appliance_id": "appl_299"}}]`
- **Nhãn mới:** `[{"name": "appliances.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "appliances.stop", "params": ["appliance_id"]}}]`

## [ ] train_1632#d1 (C)

- **Gốc:** Ông Nathan Reed muốn bán cô hai chỉ vàng nhẫn, coi giá mua vô bao nhiêu, rồi nhắc cô bảy giờ tối gọi ổng nha.
- **Mới:** Ông Nathan Reed muốn bán cô hai chỉ vàng nhẫn, coi giá mua vô bao nhiêu, rồi nhắc cô gọi ổng nha.
- **Nhãn gốc:** `[{"name": "gold_price.get_price", "arguments": {"type": "ring"}}, {"name": "reminders.create", "arguments": {"content": "gọi ông Nathan Reed", "time": "2026-11-27T19:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "gold_price.get_price", "arguments": {"type": "ring"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1105#d1 (C)

- **Gốc:** Mình muốn đổi giờ giao cái ốp lưng điện thoại qua chín giờ sáng mai, được không hè?
- **Mới:** Mình muốn đổi giờ giao cái ốp lưng điện thoại, được không hè?
- **Nhãn gốc:** `[{"name": "package_tracking.track", "arguments": {}}, {"name": "package_tracking.reschedule_delivery", "arguments": {"tracking_id": "JV567871861", "time": "2026-10-15T09:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "package_tracking.track", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "package_tracking.reschedule_delivery", "params": ["time"]}}]`

## [ ] train_1362#d1 (B-vague)

- **Gốc:** Giờ lấy hàng bên Evergreen Foods mà còn chưa tới một tiếng nữa thì gọi video cho bên đó, không thì gọi thường nha.
- **Mới:** Giờ lấy hàng bên Evergreen mà còn chưa tới một tiếng nữa thì gọi video cho bên đó, không thì gọi thường nha.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.call", "arguments": {"chat_id": "chat_6391", "video": true}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.call", "params": ["chat_id"]}}]`

## [ ] train_1631#d1 (C)

- **Gốc:** Việc lau nhà lúc sáng em bảo chưa ai nhận, giao cho Mẹ nhé, với thêm lịch check-in khách sạn hai giờ chiều mai.
- **Mới:** Việc lau nhà lúc sáng em bảo chưa ai nhận, giao cho Mẹ nhé, với thêm lịch check-in khách sạn chiều mai.
- **Nhãn gốc:** `[{"name": "household_chores.assign", "arguments": {"chore_id": "chore_5129", "assignee": "Mẹ"}}, {"name": "calendar.create_event", "arguments": {"title": "Check-in khách sạn", "start": "2026-10-17T14:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "household_chores.assign", "arguments": {"chore_id": "chore_5129", "assignee": "Mẹ"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.create_event", "params": ["start"]}}]`

## [ ] train_0615#d1 (C)

- **Gốc:** Đăng ký cho em khóa Sơ cứu gia đình nha, xong thêm buổi khai giảng lúc bảy giờ tối thứ hai, mùng năm tháng mười vào lịch cá nhân của em giúp em.
- **Mới:** Đăng ký cho em khóa Sơ cứu gia đình nha, xong thêm buổi khai giảng vào lịch cá nhân của em giúp em.
- **Nhãn gốc:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "learning.enroll", "arguments": {"course_id": "course_04"}}, {"name": "calendar.create_event", "arguments": {"title": "Khai giảng sơ cứu", "start": "2026-10-05T19:00:00+07:00", "end": "2026-10-05T20:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "learning.enroll", "arguments": {"course_id": "course_04"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.create_event", "params": ["start"]}}]`

## [ ] train_1621#d1 (B-vague)

- **Gốc:** Chị vừa học khoá Luyện nói giọng London từ hai rưỡi đến ba giờ mười lăm chiều, em ghi lại tiến độ giúp chị nhé.
- **Mới:** Chị vừa học khoá Luyện nói từ hai rưỡi đến ba giờ mười lăm chiều, em ghi lại tiến độ giúp chị nhé.
- **Nhãn gốc:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "learning.log_progress", "arguments": {"course_id": "course_742", "minutes": 45}}]`
- **Nhãn mới:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "learning.log_progress", "params": ["course_id"]}}]`

## [ ] train_0965#d1 (B-vague)

- **Gốc:** Ra chợ lấy hàng nè con, đặt cô chiếc xe đạp thể thao ở trạm gần nhà nha.
- **Mới:** Ra chợ lấy hàng nè con, đặt cô chiếc xe đạp ở trạm gần nhà nha.
- **Nhãn gốc:** `[{"name": "bike_rental.find_bikes", "arguments": {"near": "Lê Văn Sỹ"}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_251"}}]`
- **Nhãn mới:** `[{"name": "bike_rental.find_bikes", "arguments": {"near": "Lê Văn Sỹ"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "bike_rental.reserve", "params": ["bike_id"]}}]`

## [ ] train_1359#d1 (B-vague)

- **Gốc:** Em ghi tiến độ khoá học bên Quantum Leap Academy cho anh, đúng bằng thời gian buổi webinar tối qua nha.
- **Mới:** Em ghi tiến độ khoá học cho anh, đúng bằng thời gian buổi webinar tối qua nha.
- **Nhãn gốc:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "learning.log_progress", "arguments": {"course_id": "course_2093", "minutes": 75}}]`
- **Nhãn mới:** `[{"name": "learning.list_courses", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "learning.log_progress", "params": ["course_id"]}}]`

## [ ] train_0799#d1 (B-vague)

- **Gốc:** Ngoài trời giờ thế nào hả chị, nếu đang mưa hay lạnh dưới mười tám độ thì bật máy sấy chăn chạy chế độ sấy nhanh cho em nhé.
- **Mới:** Ngoài trời giờ thế nào hả chị, nếu đang mưa hay lạnh dưới mười tám độ thì bật máy sấy chạy chế độ sấy nhanh cho em nhé.
- **Nhãn gốc:** `[{"name": "weather.get_current", "arguments": {}}, {"name": "appliances.list", "arguments": {}}, {"name": "appliances.start_cycle", "arguments": {"appliance_id": "appl_06", "cycle": "quick"}}]`
- **Nhãn mới:** `[{"name": "weather.get_current", "arguments": {}}, {"name": "appliances.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "appliances.start_cycle", "params": ["appliance_id"]}}]`

## [ ] train_0771#d1 (C)

- **Gốc:** Ở phòng khách có mấy cái máy lọc không khí đó, cái nào đang chạy mà công suất dưới năm mươi oát thì cài cho nó tự tắt lúc mười một giờ mười lăm tối hằng ngày giúp chị nha.
- **Mới:** Ở phòng khách có mấy cái máy lọc không khí đó, cái nào đang chạy mà công suất dưới năm mươi oát thì cài cho nó tự tắt hằng ngày giúp chị nha.
- **Nhãn gốc:** `[{"name": "smart_home.get_status", "arguments": {"room": "phòng khách"}}, {"name": "home_automation.create_rule", "arguments": {"device_id": "purifier_living", "action": "off", "time": "23:15", "title": "Tắt máy lọc không khí 42W phòng khách"}}]`
- **Nhãn mới:** `[{"name": "smart_home.get_status", "arguments": {"room": "phòng khách"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "home_automation.create_rule", "params": ["time"]}}]`

## [ ] train_0301#d1 (C)

- **Gốc:** Nhắc mình tắt bếp lúc 8 giờ kém 15 sáng mai nha.
- **Mới:** Nhắc mình tắt bếp sáng mai nha.
- **Nhãn gốc:** `[{"name": "reminders.create", "arguments": {"content": "tắt bếp", "time": "2026-11-10T07:45:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1702#d1 (B-vague)

- **Gốc:** Con ơi, playlist ni nghe chán rồi, mở bài mô của Đức Phúc cho cô nghe.
- **Mới:** Con ơi, playlist ni nghe chán rồi, mở bài mô cho cô nghe.
- **Nhãn gốc:** `[{"name": "music.list_tracks", "arguments": {}}, {"name": "music.play", "arguments": {"track_id": "trk_1264"}}]`
- **Nhãn mới:** `[{"name": "music.list_tracks", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "music.play", "params": ["track_id"]}}]`

## [ ] train_1519#d1 (B-vague)

- **Gốc:** Dọn nhà vệ sinh giao cho Bé Na, còn nhận thùng hàng bên Marigold Foods thì giao chú Năm nha con.
- **Mới:** Dọn nhà vệ sinh giao cho Bé Na, còn việc hàng bên Marigold thì giao chú Năm nha con.
- **Nhãn gốc:** `[{"name": "household_chores.list_chores", "arguments": {}}, {"name": "household_chores.assign", "arguments": {"chore_id": "chore_1602", "assignee": "Bé Na"}}, {"name": "household_chores.assign", "arguments": {"chore_id": "chore_3318", "assignee": "Chú Năm"}}]`
- **Nhãn mới:** `[{"name": "household_chores.list_chores", "arguments": {}}, {"name": "household_chores.assign", "arguments": {"chore_id": "chore_1602", "assignee": "Bé Na"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "household_chores.assign", "params": ["chore_id"]}}]`

## [ ] train_1508#d1 (B-vague)

- **Gốc:** Sữa tươi Hằng mua rồi đó, xoá khỏi danh sách đi chợ giùm tôi nghen.
- **Mới:** Sữa Hằng mua rồi đó, xoá khỏi danh sách đi chợ giùm tôi nghen.
- **Nhãn gốc:** `[{"name": "shopping_list.get", "arguments": {}}, {"name": "shopping_list.remove", "arguments": {"item_id": "item_2258"}}]`
- **Nhãn mới:** `[{"name": "shopping_list.get", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "shopping_list.remove", "params": ["item_id"]}}]`

## [ ] train_1196#d1 (B-vague)

- **Gốc:** Chị kẹt họp tổ rồi. Năm giờ nhắc chị gọi Minh nhé, với xem trạm gần bể bơi có xe đạp thường không, có thì đặt cho con một chiếc.
- **Mới:** Chị kẹt họp tổ rồi. Năm giờ nhắc chị gọi Minh nhé, với xem trạm gần bể bơi có xe đạp không, có thì đặt cho con một chiếc.
- **Nhãn gốc:** `[{"name": "reminders.create", "arguments": {"content": "Gọi cho Minh", "time": "2026-10-13T17:00:00+07:00"}}, {"name": "bike_rental.find_bikes", "arguments": {"near": "Láng Hạ"}}, {"name": "bike_rental.reserve", "arguments": {"bike_id": "bike_9544"}}]`
- **Nhãn mới:** `[{"name": "reminders.create", "arguments": {"content": "Gọi cho Minh", "time": "2026-10-13T17:00:00+07:00"}}, {"name": "bike_rental.find_bikes", "arguments": {"near": "Láng Hạ"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "bike_rental.reserve", "params": ["bike_id"]}}]`

## [ ] train_1423#d1 (C)

- **Gốc:** Rồi nhắc tôi sáu giờ sáng hôm trước ngày xe lấy hàng đơn Amsterdam, kêu bạn hái xoài nha.
- **Mới:** Rồi nhắc tôi hôm trước ngày xe lấy hàng đơn Amsterdam, kêu bạn hái xoài nha.
- **Nhãn gốc:** `[{"name": "reminders.create", "arguments": {"content": "Kêu bạn hái xoài", "time": "2026-12-13T06:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_1012#d1 (C)

- **Gốc:** Con ơi, làm thủ tục chuyến bay sáng mai vô Sài Gòn cho cô, rồi đặt báo thức ba giờ rưỡi sáng giùm cô nghe.
- **Mới:** Con ơi, làm thủ tục chuyến bay sáng mai vô Sài Gòn cho cô, rồi đặt báo thức sớm giùm cô nghe.
- **Nhãn gốc:** `[{"name": "flights.my_bookings", "arguments": {}}, {"name": "flights.check_in", "arguments": {"booking_id": "bk_731"}}, {"name": "alarm.create", "arguments": {"time": "2026-10-24T03:30:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "flights.my_bookings", "arguments": {}}, {"name": "flights.check_in", "arguments": {"booking_id": "bk_731"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "alarm.create", "params": ["time"]}}]`

## [ ] train_1295#d1 (C)

- **Gốc:** Ừ, tắt dùm tôi. Mai chở hàng lên chợ, dầu mà còn dưới hai chục thì kêu tôi dậy bốn giờ, đổ đầy thùng rồi đi.
- **Mới:** Ừ, tắt dùm tôi. Mai chở hàng lên chợ, dầu mà còn dưới hai chục thì kêu tôi dậy sớm, đổ đầy thùng rồi đi.
- **Nhãn gốc:** `[{"name": "smart_home.light_set", "arguments": {"device_id": "light_kitchen", "power": "off"}}, {"name": "fuel_price.get_price", "arguments": {"type": "diesel"}}, {"name": "alarm.create", "arguments": {"time": "2026-11-15T04:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "smart_home.light_set", "arguments": {"device_id": "light_kitchen", "power": "off"}}, {"name": "fuel_price.get_price", "arguments": {"type": "diesel"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "alarm.create", "params": ["time"]}}]`

## [ ] train_1734#d1 (C)

- **Gốc:** Lưu bài báo điện thoại gập, à không, bài lãi suất tiết kiệm tăng nhẹ, với đặt báo thức chín giờ tối anh đọc nha.
- **Mới:** Lưu bài báo điện thoại gập, à không, bài lãi suất tiết kiệm tăng nhẹ, với đặt báo thức để anh đọc nha.
- **Nhãn gốc:** `[{"name": "news.search", "arguments": {"query": "lãi suất tiết kiệm"}}, {"name": "news.save", "arguments": {"article_id": "art_197"}}, {"name": "alarm.create", "arguments": {"time": "2026-11-26T21:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "news.search", "arguments": {"query": "lãi suất tiết kiệm"}}, {"name": "news.save", "arguments": {"article_id": "art_197"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "alarm.create", "params": ["time"]}}]`

## [ ] train_0741#d1 (B-vague)

- **Gốc:** Việc sắp lại cái kệ dụng cụ ấy, giao cho Thành làm đi nha.
- **Mới:** Cái việc nhà ấy, giao cho Thành làm đi nha.
- **Nhãn gốc:** `[{"name": "household_chores.list_chores", "arguments": {}}, {"name": "household_chores.assign", "arguments": {"chore_id": "chore_04", "assignee": "Thành"}}]`
- **Nhãn mới:** `[{"name": "household_chores.list_chores", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "household_chores.assign", "params": ["chore_id"]}}]`

## [ ] train_0731#d1 (C)

- **Gốc:** Thế cài cho anh cái hẹn giờ, tối nào mười giờ cũng tự tắt cái đèn đó đi nhé.
- **Mới:** Thế cài cho anh cái hẹn giờ, tối nào cũng tự tắt cái đèn đó đi nhé.
- **Nhãn gốc:** `[{"name": "home_automation.create_rule", "arguments": {"device_id": "light_reading", "action": "off", "time": "22:00", "title": "Tắt đèn đọc sách lúc 22 giờ"}}]`
- **Nhãn mới:** `[{"name": "sys.ask_missing_info", "arguments": {"tool_name": "home_automation.create_rule", "params": ["time"]}}]`

## [ ] train_1389#d1 (B-vague)

- **Gốc:** Em dời cái báo thức đi đổ xăng sớm lên nửa tiếng, rồi nhắn Peter Collins là mai mưa, nhớ mang ô nhé.
- **Mới:** Em dời cái báo thức đi đổ xăng sớm lên nửa tiếng, rồi nhắn là mai mưa, nhớ mang ô nhé.
- **Nhãn gốc:** `[{"name": "alarm.update", "arguments": {"alarm_id": "alm_03", "time": "2026-12-06T05:30:00+07:00"}}, {"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.send_message", "arguments": {"chat_id": "chat_2217", "content": "Mai mưa, nhớ mang ô."}}]`
- **Nhãn mới:** `[{"name": "alarm.update", "arguments": {"alarm_id": "alm_03", "time": "2026-12-06T05:30:00+07:00"}}, {"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.send_message", "params": ["chat_id"]}}]`

## [ ] train_1275#d1 (C)

- **Gốc:** Tám chục ký, sáu mươi lăm ngàn một ký. Cộng chung tiền xoài luôn, rồi nhắc tôi bảy giờ tối nay đem tiền qua anh Mười hen.
- **Mới:** Tám chục ký, sáu mươi lăm ngàn một ký. Cộng chung tiền xoài luôn, rồi nhắc tôi đem tiền qua anh Mười hen.
- **Nhãn gốc:** `[{"name": "calculator.calculate", "arguments": {"expression": "80*65000+5400000"}}, {"name": "reminders.create", "arguments": {"content": "Đem tiền qua trả anh Mười", "time": "2026-12-11T19:00:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "calculator.calculate", "arguments": {"expression": "80*65000+5400000"}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "reminders.create", "params": ["time"]}}]`

## [ ] train_0040#d1 (B-vague)

- **Gốc:** Ơi, dời lịch cà phê với gia đình mai muộn hơn nửa tiếng giúp chị nhé.
- **Mới:** Ơi, dời lịch cà phê muộn hơn nửa tiếng giúp chị nhé.
- **Nhãn gốc:** `[{"name": "calendar.list_events", "arguments": {}}, {"name": "calendar.update_event", "arguments": {"event_id": "evt_02", "start": "2026-11-10T15:30:00+07:00", "end": "2026-11-10T16:30:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "calendar.list_events", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "calendar.update_event", "params": ["event_id"]}}]`

## [ ] train_1462#d1 (B-vague)

- **Gốc:** Quãng đó mà dưới hai cây số thì em ghi vô ghi chú khách Hàn là đi bộ, không thì ghi đi taxi nghe.
- **Mới:** Quãng đó mà dưới hai cây số thì em ghi vô ghi chú là đi bộ, không thì ghi đi taxi nghe.
- **Nhãn gốc:** `[{"name": "notes.list", "arguments": {}}, {"name": "notes.append", "arguments": {"note_id": "note_9014", "content": "đi bộ"}}]`
- **Nhãn mới:** `[{"name": "notes.list", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "notes.append", "params": ["note_id"]}}]`

## [ ] train_1213#d1 (B-vague)

- **Gốc:** Khoá ngoại ngữ anh đang theo á, xếp lẹ một buổi học ngay lúc mai chạy Vũng Tàu xong.
- **Mới:** Khoá học anh đang theo á, xếp lẹ một buổi học ngay lúc mai chạy Vũng Tàu xong.
- **Nhãn gốc:** `[{"name": "calendar.list_events", "arguments": {"date_from": "2026-10-14", "date_to": "2026-10-14"}}, {"name": "learning.list_courses", "arguments": {}}, {"name": "learning.schedule_lesson", "arguments": {"course_id": "course_726", "time": "2026-10-14T11:30:00+07:00"}}]`
- **Nhãn mới:** `[{"name": "calendar.list_events", "arguments": {"date_from": "2026-10-14", "date_to": "2026-10-14"}}, {"name": "learning.list_courses", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "learning.schedule_lesson", "params": ["course_id"]}}]`

## [ ] train_0034#d1 (B-vague)

- **Gốc:** Ờ à, nhắn qua Zalo cho bác Ba là tối nay ăn cơm ở nhà nhé.
- **Mới:** Ờ à, nhắn qua Zalo là tối nay ăn cơm ở nhà nhé.
- **Nhãn gốc:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "chat_ott.send_message", "arguments": {"chat_id": "chat_04", "content": "tối nay ăn cơm ở nhà nhé"}}]`
- **Nhãn mới:** `[{"name": "chat_ott.list_chats", "arguments": {}}, {"name": "sys.ask_missing_info", "arguments": {"tool_name": "chat_ott.send_message", "params": ["chat_id"]}}]`
