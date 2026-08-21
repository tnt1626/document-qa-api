import asyncio
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.services.rag.embedder import embed_text
from app.services.rag.chunker import chunk_text
from app.services.rag.generator import generate


async def main():
    content = """Việt Nam, quốc hiệu đầy đủ là Cộng hòa xã hội chủ nghĩa Việt Nam,[12] là một quốc gia nằm ở cực Đông của bán đảo Đông Dương thuộc khu vực Đông Nam Á, giáp với Lào, Campuchia, Trung Quốc, biển Đông và vịnh Thái Lan.

Lãnh thổ Việt Nam xuất hiện con người sinh sống từ thời đại đồ đá cũ, khởi đầu với các nhà nước Văn Lang, Âu Lạc. Âu Lạc bị nhà Triệu ở phương Bắc thôn tính vào đầu thế kỷ thứ 2 TCN sau đó là thời kỳ Bắc thuộc kéo dài hơn một thiên niên kỷ. Chế độ quân chủ độc lập được tái lập sau chiến thắng của Ngô Quyền trước nhà Nam Hán, mở đường cho các triều đại độc lập kế tục, nhiều lần chiến thắng trước các cuộc chiến tranh xâm lược từ phương Bắc đồng thời dần mở rộng về phía nam. Thời kỳ Bắc thuộc cuối cùng kết thúc sau chiến thắng trước nhà Minh của nghĩa quân Lam Sơn.

Đến thời cận đại, Việt Nam lần lượt trải qua các giai đoạn Pháp thuộc và Nhật thuộc. Sau khi đánh bại và buộc Nhật Bản đầu hàng, khối Đồng Minh tạo điều kiện cho Pháp thu hồi Liên bang Đông Dương. Kết thúc Thế chiến II, Việt Nam chịu sự can thiệp của các nước Đồng Minh bao gồm Anh, Pháp (miền Nam), Trung Hoa Dân Quốc (miền Bắc). Nhà nước Việt Nam Dân chủ Cộng hòa do Việt Minh lãnh đạo ra đời khi Hồ Chí Minh tuyên bố độc lập vào ngày 2 tháng 9 năm 1945 sau thành công của Cách mạng Tháng Tám và chiến thắng Liên hiệp Pháp cùng Quốc gia Việt Nam do Pháp hậu thuẫn trong chiến tranh Đông Dương lần thứ nhất. Sự kiện này dẫn tới Hiệp định Genève (1954) được ký kết và Việt Nam bị chia cắt thành hai vùng tập kết quân sự, lấy ranh giới là vĩ tuyến 17. Việt Nam Dân chủ Cộng hòa kiểm soát phần phía bắc còn phía nam do Việt Nam Cộng hòa (nhà nước kế tục Quốc gia Việt Nam) kiểm soát và được Hoa Kỳ hậu thuẫn. Xung đột về thống nhất lãnh thổ đã dẫn tới chiến tranh Việt Nam với sự can thiệp của nhiều nước và kết thúc với chiến thắng của Việt Nam Dân chủ Cộng hòa, Mặt trận Dân tộc Giải phóng miền Nam Việt Nam cùng sự sụp đổ của Việt Nam Cộng hòa vào năm 1975. Chủ quyền phần phía Nam được chính quyền Cộng hòa miền Nam Việt Nam (do Mặt trận Dân tộc Giải phóng miền Nam Việt Nam thành lập) giành quyền kiểm soát. Năm 1976, Việt Nam Dân chủ Cộng hòa và Cộng hòa miền Nam Việt Nam thống nhất thành Cộng hòa xã hội chủ nghĩa Việt Nam.

Sau khi tái thống nhất, Việt Nam tiếp tục gặp khó khăn do sự sụp đổ và tan rã của đồng minh Liên Xô cùng Khối phía Đông, các lệnh cấm vận của Hoa Kỳ,[13] chiến tranh Đông Dương lần ba và hậu quả của chính sách bao cấp sau nhiều năm áp dụng. Năm 1986, Đảng Cộng sản Việt Nam ban hành cải cách đổi mới, xây dựng kinh tế thị trường và hội nhập sâu rộng. Cải cách kinh tế cùng quy mô dân số lớn đưa Việt Nam trở thành một trong những nước đang phát triển có tốc độ tăng trưởng thuộc nhóm nhanh nhất thế giới, được coi là Hổ mới châu Á dù cho vẫn gặp phải những thách thức như tham nhũng[14] và phúc lợi xã hội chưa đầy đủ.[15] Ngoài ra, giới bất đồng chính kiến và các tổ chức theo dõi nhân quyền có quan điểm chỉ trích hồ sơ nhân quyền của Việt Nam liên quan đến các vấn đề tôn giáo, kiểm duyệt truyền thông và tự do dân sự.[16]
Tên gọi
Nguồn gốc tên gọi
Bài chi tiết: Tên gọi Việt Nam

Các nhà nước trong lịch sử Việt Nam có những quốc hiệu khác nhau như Xích Quỷ, Văn Lang, Đại Việt, Đại Nam hay Việt Nam. Chữ Việt Nam (越南) được cho là việc đổi ngược lại của quốc hiệu Nam Việt (南越) thời Triệu Vũ Ðế. Chữ "Việt" 越 đặt ở đầu biểu thị đất Việt Thường, cương vực cũ của nước này, từng được dùng trong các quốc hiệu Đại Cồ Việt (大瞿越) và Đại Việt (大越), là các quốc hiệu từ thế kỷ 10 tới đầu thế kỷ 19. Chữ "Nam" 南 đặt ở cuối thể hiện đây là vùng đất phía nam, là vị trí cương vực, từng được dùng cho quốc hiệu Đại Nam (大南), và trước đó là một cách gọi phân biệt Đại Việt là Nam Quốc (như "Nam Quốc Sơn Hà") với Bắc Quốc là Trung Hoa.[cần dẫn nguồn]

Vua Gia Long nhà Nguyễn chính thức sử dụng quốc hiệu "Việt Nam" từ năm 1804.[17] Sau đó Nhà Thanh công nhận Việt Nam là quốc hiệu của Nhà Nguyễn.[18] Đặt quốc hiệu là "Việt Nam" để không nhầm với nước Nam Việt, cũng như thể hiện vị trí địa lý nằm ở phía nam Bách Việt. Trùng hợp là trước đó mấy trăm năm, trong Sấm Trạng Trình Nguyễn Bỉnh Khiêm đã dùng tên "Việt Nam" làm tên chính thức, mặc dù khi đó vẫn còn sử dụng quốc hiệu "Đại Việt". Năm 1804, vua Thanh cho án sát sứ Quảng Tây Tề Bố Sâm sang tuyên phong Gia Long làm "Việt Nam quốc vương" 越南國王 mặc dù các vua nhà Nguyễn vẫn theo lệ cũ tự phong "Hoàng đế" 皇帝 cho ngang hàng với vua Trung Quốc.[19][20]

Tên gọi "Việt Nam" cũng xuất hiện trong tác phẩm Việt Nam vong quốc sử của Phan Bội Châu năm 1905 và trong tên gọi Việt Nam Quốc dân Đảng.[21] Tên gọi "An Nam" cũng có trong thời Pháp thuộc. Năm 1945, Đế quốc Việt Nam ra đời và tiếp tục đặt quốc hiệu "Việt Nam".[22] Sau đó tất cả những nhà nước ở Việt Nam sau năm 1945 đều sử dụng quốc hiệu này.
Trong văn viết tiếng nước ngoài

Trong văn viết tiếng Anh hiện nay, cách viết thông dụng nhất cho tên gọi Việt Nam là Vietnam (viết liền không dấu cách cho từ ghép, là một kiểu Anh hoá tên gọi để phù hợp với cấu trúc từ vựng cũng như chính tả của tiếng Anh), dẫn đến thêm tiếp tố "-ese" để tạo ra tính từ là Vietnamese. Ở Việt Nam tồn tại thêm hai cách viết giữ dấu cách là "Viet Nam" (bỏ dấu) và "Việt Nam" (để đầy đủ dấu theo chữ Quốc ngữ). Điều này có thể nhận thấy trên website của Chính phủ Việt Nam và Bộ Ngoại giao Việt Nam cho phiên bản tiếng Anh trước đây có dùng cả 3 cách: "Vietnam", "Viet Nam" hoặc "Việt Nam".[23][24] Từ điển tiếng Anh Oxford mới chỉ ghi nhận cách viết Vietnam cho danh từ và Vietnamese cho tính từ,[25][26] chưa có ghi nhận "Viet Nam" và "Viet Namese".[27][28] Danh sách liệt kê thành viên trên trang web của Liên Hợp Quốc viết tên quốc gia này là "Viet Nam" trong khi các bài viết tiểu mục thì vẫn viết là "Vietnam". Còn Bộ Ngoại giao Việt Nam và Tổ chức tiêu chuẩn hóa quốc tế (ISO) thì sử dụng "Viet Nam" và quốc hiệu "the Socialist Republic of Viet Nam" như là tên gọi tiêu chuẩn trên các văn bản tiếng nước ngoài, chủ yếu trên các văn bản và văn hóa phẩm tiếng Anh được phát hành bởi Nhà nước Việt Nam.[29][30] Nhìn chung, cả "Vietnam" hay "Viet Nam" đều được chấp nhận trong tiếng Anh, trong đó "Vietnam" được dùng phổ biến hơn trong các phương tiện truyền thông từ nước ngoài.

Với hầu hết ngôn ngữ khác dùng chữ Latinh như tiếng Tây Ban Nha, tiếng Đức, tiếng Ý,... chủ yếu cũng sử dụng cách viết "Vietnam", và một số ngôn ngữ có cách viết khác như "Vietnã" (tiếng Bồ Đào Nha), "Wietnam" (tiếng Ba Lan), "Vítneam" (tiếng Ireland), tuỳ vào cấu trúc bảng chữ cái Latinh của mỗi ngôn ngữ, nhưng đều viết liền không dấu cách. Các ngôn ngữ khác dùng những hệ chữ viết có họ hàng gần với chữ Latinh như chữ Cyrill hay chữ Hy Lạp cũng thường viết liền không dấu cách để chỉ Việt Nam như "Вьетнам" (tiếng Nga), "Вијетнам" (tiếng Serbia), "Βιετνάμ" (tiếng Hy Lạp).[31][32]
Lịch sử
Bài chi tiết: Lịch sử Việt Nam
Sự khuếch trướng lãnh thổ của các triều đại người Việt từ thời nhà Lý (1009) cho đến hết nhà Nguyễn (1945) cùng với công cuộc Nam tiến (1069–1757)

Các nhà khảo cổ học tìm thấy những dấu vết của người đứng thẳng thời đồ đá cũ trên lãnh thổ Việt Nam cách đây khoảng 500.000 năm; các công cụ thô sơ bằng đá và các dấu răng của người tiền sử được phát hiện tại các tỉnh Lạng Sơn, Thanh Hóa, Yên Bái, Ninh Bình và Quảng Bình[33] Ngoài ra, tại các vùng phía Bắc, con người sinh sống trong các hang động đá vôi và sống bằng các hoạt động săn thú, hái lượm. Trong khi đó, tại các vùng duyên hải miền Trung như Nghệ An, con người chủ yếu sống bằng đánh cá.[33]

Đến thời đại đồ đá mới cách đây 5000 đến 6000 năm, người Việt cổ bắt đầu biết canh tác lúa nước; loạt dấu vết trồng lúa có từ cao nguyên tới đồng bằng.[33] Ngoài ra, con người bắt đầu biết chế tác công cụ theo kiểu khác và làm đồ gốm với kỹ thuật khác.[33] Đến khoảng thiên niên kỷ I TCN vào cuối thời kỳ đồ đồng, khu vực lúa nước ở sông Hồng và sông Cả phát triển thành nền văn hóa Đông Sơn[34] rồi cùng thời gian đó, những nhà nước đầu tiên lần lượt xuất hiện đó là Văn Lang và Âu Lạc.[35]

Từ thế kỷ II TCN, các triều đại phong kiến từ phương Bắc cai trị một phần Việt Nam hơn 1000 năm.[36] Sự cai trị này bị ngắt quãng bởi những cuộc khởi nghĩa của những tướng lĩnh như Bà Triệu, Mai Thúc Loan, Hai Bà Trưng hay Lý Bí. Năm 905, Khúc Thừa Dụ giành quyền tự chủ, không phải là độc lập vì Dụ tự nhận mình là quan triều đình phương Bắc.[37] Đến năm 938, sau khi chỉ huy trận sông Bạch Đằng đánh bại quân Nam Hán,[38] Ngô Quyền lập triều xưng vương, đánh dấu một nhà nước độc lập khỏi các triều đình phương Bắc vào năm 939.

Sau nhà Ngô, lần lượt các triều Đinh, Tiền Lê, Lý và Trần tổ chức chính quyền tương tự các triều đại Trung Hoa, lấy Phật giáo làm tôn giáo chính của quốc gia và cho truyền bá cả Nho giáo và Đạo giáo. Nhà Tiền Lê, Lý và Trần đã chống trả các cuộc tấn công của nhà Tống và nhà Mông – Nguyên, đều thắng lợi và bảo vệ được Đại Việt. Năm 1400, Hồ Quý Ly cướp ngôi nhà Trần, lập nhà Hồ, đổi tên nước là Đại Ngu, tiến hành cải cách. Năm 1407, Đại Ngu bị Nhà Minh thôn tính. một số thành viên hoàng tộc nhà Trần khởi nghĩa, lập nhà Hậu Trần và bị quân Minh đánh bại sau 7 năm. Năm 1427, Lê Lợi đánh đuổi quân Minh, lập nhà Hậu Lê, giành lại độc lập (năm 1428). Có quan điểm cho rằng đây là triều đại mà phong kiến Việt Nam đạt "đỉnh cao" đặc biệt là đời vua Lê Thánh Tông (1460–1497).[39]

Vào đầu thế kỷ XVI, Nhà Lê sơ bị Nhà Mạc cướp ngôi nên một bộ phận quan lại trung thành đã lập người khác trong dòng dõi vua Lê lên làm vua, tái lập Nhà Lê. Nhà Lê trung hưng sau 60 năm giao tranh đã chiến thắng, diệt Nhà Mạc. Vua Lê khi đó là bù nhìn, hai tập đoàn phong kiến Chúa Trịnh và Chúa Nguyễn tranh chấp nhau, gây chiến tranh kéo dài hơn 100 năm, chia cắt Đại Việt thành đàng Ngoài và đàng Trong trong 200 năm. Cuối thế kỷ XVIII, tướng khởi nghĩa Nguyễn Huệ trong 15 năm đã đánh bại cả Chúa Trịnh và Chúa Nguyễn cùng các cuộc xâm chiếm của Xiêm và Thanh để lập Nhà Tây Sơn. Nguyễn Huệ mất, với người kế vị Cảnh Thịnh, nhà Tây Sơn bị Nguyễn Ánh – một thành viên dòng họ Chúa Nguyễn cùng với viện trợ từ Pháp và Xiêm lật đổ, lập Nhà Nguyễn, triều đại cuối cùng ở Việt Nam.[40] Thời phong kiến, các triều Lý, Trần, Hậu Lê và chúa Nguyễn thu phục Chiêm Thành, Chân Lạp và Tây Nguyên ở phía Nam.[41]

Phương Tây tiếp cận Việt Nam từ thế kỷ XVI. Vào thế kỷ XVII, Đàng Trong và Đàng Ngoài trao đổi thương mại trước hết với Bồ Đào Nha và Hà Lan,[42] sau thêm Anh và Pháp. Các tu sĩ Dòng Tên do Bồ Đào Nha bảo trợ[43] đến truyền bá Công giáo từ năm 1615 rồi Hội Thừa sai Paris và Dòng Đa Minh tiếp nối. Công giáo tại Việt Nam phát triển trong 2 thế kỷ tiên khởi XVII và XVIII.[44] Từ thời Gia Long, Nhà Nguyễn bế quan tỏa cảng, cấm ngoại thương, không tiếp xúc công nghệ tiên tiến. Nửa sau thế kỷ 19, Pháp xâm lược bán đảo Đông Dương, thâu tóm nhà Nguyễn và thành lập Liên bang Đông Dương năm 1887. Thời Pháp thuộc, văn hóa, khoa học, kỹ thuật từ phương Tây được tăng cường truyền bá.[45]
Lễ tuyên bố thành lập nhà nước Việt Nam Dân chủ Cộng hòa tại quảng trường Ba Đình (1945)

Thế chiến thứ 2, Nhật đảo chính Pháp ở Đông Dương, dựng nên Đế quốc Việt Nam, chính thể bù nhìn này phải nộp thuế và cung ứng cho Nhật tài nguyên có lúa gạo, góp phần gây nạn đói Ất Dậu. Sau khi Nhật đầu hàng Đồng Minh, Hồ Chí Minh lãnh đạo Việt Minh giành chính quyền, đọc Tuyên ngôn Độc lập thành lập Việt Nam Dân chủ Cộng hòa ngày 2 tháng 9 năm 1945.[46] Pháp tính lấy lại Đông Dương, nhưng vấp phải sự phản kháng của Việt Nam Dân chủ Cộng hòa nên đã buộc phải hậu thuẫn lập Quốc gia Việt Nam do Bảo Đại, cựu hoàng đế Nhà Nguyễn làm Quốc trưởng.[47]

Năm 1954, Chiến tranh Đông Dương kết thúc, Pháp phải công nhận sự độc lập của Việt Nam và rút quân, xuất hiện 2 vùng tập kết quân sự chờ cuộc bầu cử thống nhất đất nước[48] nhưng không thành do Hoa Kỳ hậu thuẫn cho Việt Nam Cộng hòa (chính phủ kế thừa Quốc gia Việt Nam) từ chối tổ chức bầu cử.[49] Nhà nước xã hội chủ nghĩa Việt Nam Dân chủ Cộng hòa hậu thuẫn các lực lượng miền Nam nổi dậy chống Chính phủ Việt Nam Cộng hòa, gây ra xung đột quân sự mà tiếp theo đó là sự tham chiến của quân đội Hoa Kỳ và đồng minh.[50] Chiến tranh kết thúc vào ngày 30 tháng 4 năm 1975 khi Tổng thống Việt Nam Cộng hòa tuyên bố đầu hàng.[51]

Năm 1976, Cộng hòa Miền Nam Việt Nam và Việt Nam Dân chủ Cộng hòa tổ chức tuyển cử hợp nhất. Do hậu quả chiến tranh, rồi chiến tranh biên giới phía Bắc, chiến tranh biên giới Tây Nam, chính sách bao cấp và bị Hoa Kỳ cấm vận, nước Việt Nam thời hậu chiến phải đối mặt với các vấn đề nghiêm trọng trong lĩnh vực kinh tế-xã hội.[52] Năm 1986, Đại hội Đảng lần VI chấp thuận Đổi mới, cải tổ nhà nước và chuyển nền kinh tế theo hướng mới.[53] Việt Nam bình thường hóa quan hệ với Hoa Kỳ năm 1995 và gia nhập ASEAN vào cùng năm. Năm 2007, Việt Nam gia nhập tổ chức kinh tế thế giới WTO"""

    async with engine.connect() as conn:
        result = await conn.execute(
            text("INSERT INTO documents (filename, content) VALUES (:filename, :content) RETURNING id"),
            {"filename": "test_1.txt", "content": content}
        )
        doc_id = result.scalar()
        await conn.commit()

    chunks = chunk_text(content)
    idx = 0
    for chunk in chunks:
        vec = await embed_text(chunk)
        async with engine.connect() as conn:
            await conn.execute(
                text("INSERT INTO chunks (document_id, content, embedding, chunk_index) values (:doc_id, :content, :embed, :idx)"),
                {"doc_id": doc_id, "content": chunk, "embed": str(vec), "idx": idx}
            )
            await conn.commit()
        idx += 1

    question = "Việt Nam giáp với những nước nào?"
    async with SessionLocal() as session:
        answer = await generate(question, doc_id, 5, session)
    print(answer)

asyncio.run(main())