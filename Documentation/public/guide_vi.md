# Hướng dẫn công khai — Financial Adviser

Tài liệu này giải thích mục đích, giả định toán học, ví dụ minh họa, cách đọc kết quả và giới hạn của công cụ. Đây là nội dung giáo dục, không phải tư vấn tài chính cá nhân.

## 1. Mục tiêu và phạm vi

**Financial Adviser** giúp khảo sát thu nhập, chi tiêu, tiền mặt, đầu tư, nợ và mục tiêu tài sản của một hộ gia đình trong tương lai. Người dùng có thể thay đổi giả định, so sánh kịch bản và thêm những sự kiện trong cuộc sống.

Ứng dụng không phải hệ thống theo dõi ngân hàng thời gian thực hay công cụ dự báo chắc chắn cho từng cá nhân. Mỗi kịch bản chỉ dùng **một loại tiền tệ**; đổi giữa Pháp và Việt Nam không tự động quy đổi số tiền.

### Dự phóng có thể trả lời những câu hỏi nào?

Công cụ giúp phân tích **các tình huống có điều kiện**: “Nếu thu nhập, chi tiêu và cách tiết kiệm không thay đổi đáng kể, tài sản ròng sau 10 năm sẽ thế nào?”, “Việc hỗ trợ người thân có ảnh hưởng ra sao?”, “Có thể đạt mục tiêu mà không bị thiếu tiền mặt không?”. Công cụ không lựa chọn khoản đầu tư tối ưu hay quyết định thay người dùng.

**Trước khi bắt đầu**, hãy chuẩn bị số liệu hợp lý về **thu nhập ròng hằng tháng của cả hộ**, chi tiêu thông thường **không bao gồm khoản trả nợ đã khai riêng**, tiền có thể sử dụng ngay, vốn đang đầu tư và dư nợ gốc còn lại. Số liệu gần đúng nhưng có cơ sở hữu ích hơn con số rất chi tiết nhưng thiếu thực tế. Bạn hoàn toàn có thể dùng dữ liệu giả định.

Hai hộ có thể có cùng tài sản ròng nhưng **khả năng thanh khoản** khác nhau. Tiền đang đầu tư không được tự động bán để trả một khoản chi bất ngờ. Vì vậy, cần phân biệt **tài sản ròng**, **tiền mặt** và **dòng tiền hằng tháng**.

## 2. Mô hình và phương trình

Việc mô phỏng được thực hiện theo từng tháng. Tài sản ròng danh nghĩa bằng tổng tài sản trừ dư nợ:

$$
N_m = C_m + A_m - D_m
$$

Trong đó $C_m$ là tiền mặt, $A_m$ là khoản đầu tư và $D_m$ là dư nợ tại tháng $m$.

Dòng tiền còn lại trước khi chuyển tiền sang đầu tư được biểu diễn bởi:

$$
F_m = Y_m - E_m - L_m + O_m
$$

Một tỷ suất sinh lời hiệu dụng hằng năm $R$ tương ứng với tỷ suất theo tháng:

$$
r_m = (1+R)^{1/12}-1
$$

Với lạm phát hằng năm giả định $\pi$, giá trị tài sản ròng theo sức mua tại thời điểm bắt đầu là:

$$
N_m^{\mathrm{real}} = \frac{N_m}{(1+\pi)^{m/12}}
$$

Thu nhập, chi tiêu, thanh toán và chuyển khoản được ghi nhận trước phần sinh lời của tháng. Chuyển tiền nội bộ giữa tiền mặt và đầu tư **không phải thu nhập**. Tỷ suất sinh lời, lạm phát và dòng tiền tương lai đều là giả định.

Mô phỏng Monte Carlo đơn giản chỉ minh họa sự phân tán kết quả đầu tư theo giả định đã chọn; các phân vị **không bảo đảm** kết quả trong thực tế.

### Thứ tự tính toán trong mỗi tháng

Vào đầu mỗi tháng dự phóng, thu nhập làm tăng tiền mặt; chi tiêu, khoản trả nợ và chi phí sự kiện làm giảm tiền mặt. Những khoản thu một lần được cộng vào. Sau đó, tiền dự kiến đầu tư được chuyển từ tiền mặt sang vốn đầu tư. Cuối cùng, hai khoản này mới được áp dụng mức sinh lời giả định của tháng.

Với khoản chuyển sang đầu tư $T$ mỗi tháng và tỷ suất theo tháng $r_C$, $r_A$, ta có $C_m=(C_{m-1}+F_m-T)(1+r_C)$ và $A_m=(A_{m-1}+T)(1+r_A)$. Chuyển 400 € sang đầu tư **không tạo ra thêm** 400 € tài sản: đó chỉ là chuyển tiền giữa hai loại tài sản.

**Ví dụ hoàn toàn giả định**, không có lợi tức hay sự kiện: thu nhập 3.000 €, chi tiêu thông thường 2.000 € và trả nợ 300 € thì còn 700 € trước khi chuyển tiền đầu tư. Nếu chuyển 400 €, tiền mặt tăng 300 € và vốn đầu tư tăng 400 €; đồng thời dư nợ gốc giảm theo phần gốc trong khoản thanh toán.

Thu nhập và chi tiêu cơ sở thay đổi theo giả định tăng trưởng hằng năm đã chọn. Lợi suất hiệu dụng năm và lạm phát được quy đổi thành tỷ lệ theo tháng. Riêng **lãi suất danh nghĩa năm của khoản vay** được chia cho 12 để tính lãi theo tháng. Khoản vay được mô phỏng theo lịch trả đều cho đến khi tất toán.

### Danh nghĩa, sức mua và mục tiêu

**Tài sản danh nghĩa** biểu thị số tiền tại thời điểm tương ứng. **Tài sản thực** quy về sức mua tại thời điểm bắt đầu. Ví dụ, giả sử lạm phát cố định 2%/năm, thì 100.000 € sau mười năm tương đương khoảng 82.035 € sức mua ban đầu. Đây chỉ là minh họa, không phải dự báo lạm phát.

Mục tiêu tài sản được nhập theo giá trị **danh nghĩa**. Đạt mục tiêu ở cuối kỳ không đồng nghĩa với việc tiền mặt luôn dương trong toàn bộ thời gian. Hãy kiểm tra riêng hai điều kiện này.

## 3. Nguồn dữ liệu và độ tin cậy

Ứng dụng phân biệt **thống kê quá khứ**, **giả định cho tương lai** và **quy định pháp luật**. Không nên trực tiếp sử dụng một con số trung bình toàn quốc để thay thế thu nhập hoặc chi phí của gia đình mình.

Các nguồn tham khảo chính gồm [Insee](https://www.insee.fr/fr/information/8184146), [Ngân hàng Trung ương Pháp](https://www.banque-france.fr/fr) và [Cục Thống kê Việt Nam](https://www.nso.gov.vn/en/).

Trang số liệu thống kê riêng biệt trình bày phạm vi, thời kỳ và nguồn của từng quan sát. Hệ thống hiện **không tự động tính thuế** theo luật quốc gia.

### Đọc một số liệu thống kê thế nào?

Hãy kiểm tra **đơn vị công bố**, **ngày công bố**, **giai đoạn thống kê**, **đối tượng khảo sát**, **đơn vị đo** và **định nghĩa chỉ số**. Thu nhập trung vị của một cá nhân không phải thu nhập ròng của một hộ. Chỉ số giá chung chưa chắc phản ánh chi tiêu thực tế của riêng gia đình bạn.

**Pháp và Việt Nam** có hệ thống thống kê và an sinh xã hội khác nhau. Không nên dùng trực tiếp một mức bình quân toàn quốc cho một cá nhân, hoặc chuyển nguyên con số đó sang quốc gia khác. Các thống kê chỉ giúp đặt giả định trong bối cảnh; chúng không bảo đảm kết quả của kịch bản.

Lợi suất, lương hưu và tăng lương trong tương lai vẫn phải được ghi nhận là **giả định của người dùng**, kể cả khi có giá trị gần với số liệu lịch sử. Trang “Nguồn và quy tắc” giúp phân biệt dữ liệu quan sát với những quy định chưa được đưa vào phép tính.

## 4. Nguyên tắc sử dụng

Quy trình chính gồm **nhập kế hoạch**, **điều chỉnh giả định**, **chạy mô phỏng** và **xem kết quả**.

Biểu đồ thể hiện tài sản ròng, tiền mặt, đầu tư và dư nợ. Các chỉ báo cho biết khả năng thiếu hụt tiền mặt và mức độ đạt được mục tiêu đã đặt ra. Có thể so sánh các giả định mà không tự động thay đổi kịch bản gốc.

Người dùng có thể chủ động nhập hoặc xuất kế hoạch dưới dạng JSON. Ứng dụng không tự lấy giao dịch từ ngân hàng.

### Quy trình sử dụng đề xuất

1. **Mô tả tình hình hiện tại:** thu nhập ròng của hộ, chi tiêu định kỳ, tiền mặt, vốn đầu tư, dư nợ và thời gian dự phóng.
2. **Kiểm tra chi tiêu cơ sở:** không tính lặp khoản trả nợ đã khai riêng hoặc tiền chuyển từ tài khoản sang đầu tư.
3. **Nhập những thay đổi muốn khảo sát:** các thành viên gia đình, hỗ trợ người thân, nghỉ hưu giả định và sự kiện có thời điểm cụ thể.
4. **Rà soát giả định nâng cao:** tăng trưởng thu nhập và chi tiêu, lạm phát, lợi suất và biến động. Điều chỉnh các con số minh họa cho phù hợp.
5. **Chạy dự phóng**, trước tiên xem tiền mặt thấp nhất, dư nợ và tài sản sau điều chỉnh sức mua, rồi mới xét mục tiêu tài sản.
6. **Mỗi lần thay đổi một giả định** để đánh giá mức ảnh hưởng, sau đó thử thêm các tình huống bất lợi độc lập.

### Cách hiểu các chỉ báo

**Tài sản ròng** bằng tiền mặt cộng vốn đầu tư trừ dư nợ gốc. **Số tháng dự phòng tiền mặt** lấy tiền mặt đầu kỳ chia cho chi tiêu hiện tại cộng khoản trả nợ hằng tháng: đây là chỉ báo tĩnh, không bảo đảm an toàn tài chính. **Tỷ lệ trả nợ / thu nhập ròng** không phải tỷ lệ xét duyệt tín dụng chính thức. Tài sản ròng có thể tăng ngay cả khi tiền mặt giảm.

Sau khi bạn chỉnh sửa các ô nhập, kết quả đang hiển thị có thể vẫn thuộc về **lần tính gần nhất**. Cần chạy lại trước khi kết luận. Việc xuất kịch bản chỉ lưu giả định đã nhập, không phải sao kê ngân hàng hay bằng chứng về kết quả tương lai.

## 5. So với những công cụ khác

Ứng dụng quản lý chi tiêu thường tập trung vào ngân sách hiện tại hoặc quá khứ; công cụ theo dõi danh mục tập trung vào đầu tư; công cụ lập kế hoạch khảo sát **những kịch bản tương lai có điều kiện**.

Financial Adviser tập trung vào loại thứ ba. Ứng dụng không thay thế phần mềm kế toán, dịch vụ khai thuế, tính lương hưu chính thức hoặc tư vấn đầu tư được cấp phép.

### Nên dùng công cụ cho việc gì?

| Nhu cầu | Công cụ có thể hỗ trợ | Không thể thay thế |
|---|---|---|
| Chi tiêu hằng tháng tăng thì sao? | So sánh các dự phóng có điều kiện | Ghi chép chi tiết mọi hóa đơn |
| Chuyển nhà hoặc gián đoạn thu nhập | Sự kiện có thời gian, chi phí và thay đổi thu nhập | Báo giá thực tế hay quyết định trợ cấp |
| Có đạt mục tiêu tài sản không? | So sánh mục tiêu danh nghĩa và kiểm tra tiền mặt | Tư vấn đầu tư cá nhân |
| Một thành viên nghỉ hưu | Mô phỏng lương hưu **giả định** | Xác nhận quyền hưởng lương hưu chính thức |
| Thị trường đầu tư giảm | Phân tích độ nhạy và mức phân tán mô phỏng | Dự báo thị trường hay đánh giá toàn bộ rủi ro |

So sánh kịch bản giúp hiểu **độ nhạy đối với các giả định**, không thể xác định tương lai nào sẽ xảy ra.

## 6. Giới hạn, chất lượng và quyền riêng tư

Mô hình chưa bao quát đầy đủ thuế, mọi loại phí sản phẩm, trợ cấp xã hội, tỷ giá và giá trị tài sản bất động sản chưa được khai báo.

**Tiền mặt âm** thể hiện khoản thiếu hụt chưa có nguồn tài trợ, không đồng nghĩa với việc ngân hàng chấp nhận thấu chi hay tài sản được bán tự động. Kết quả tốt không chứng minh kế hoạch chắc chắn khả thi.

Ứng dụng không yêu cầu kết nối ngân hàng. Dữ liệu nhập trên phiên bản trực tuyến vẫn được xử lý trên máy chủ trong thời gian sử dụng. Hãy dùng số liệu giả định hoặc chạy cục bộ nếu dữ liệu quá nhạy cảm.

### Những câu hỏi cần đặt ra khi xem kết quả

- **Thanh khoản:** tiền mặt có âm vào bất kỳ tháng nào không? Công cụ không tự bán tài sản đầu tư để bù thiếu hụt.
- **Tính nhất quán:** khoản trả nợ, chi phí gia đình và sự kiện có bị tính hai lần không?
- **Sức mua:** mục tiêu danh nghĩa có còn ý nghĩa sau khi tính lạm phát không?
- **Độ nhạy:** kết quả có phụ thuộc quá nhiều vào lợi suất cao hoặc tăng lương lạc quan không?
- **Mức độ đầy đủ:** còn thiếu các khoản thuế, bảo hiểm, phí, tài sản, nhà đất hoặc nghĩa vụ chi tiêu đáng kể nào không?

Công cụ dùng giả định lợi suất đơn giản và không bao quát mọi khoản phí, thuế và lịch thanh toán của sản phẩm tài chính. Nhập một khoản vay mua nhà **không tự động thêm ngôi nhà** vào tài sản. Do đó, tài sản thực tế của chủ sở hữu nhà có thể khác đáng kể số liệu đang hiển thị.

**Quyền riêng tư:** nếu không cần thiết, tránh nhập thông tin định danh hoặc số liệu nhạy cảm quá chính xác trên phiên bản trực tuyến. Không kết nối tài khoản ngân hàng không có nghĩa dữ liệu nhập không được xử lý trên dịch vụ lưu trữ ứng dụng.

## 7. Hướng phát triển có thể xem xét

Các hướng mở rộng gồm thêm loại tài sản và khoản nợ, mô hình hóa bất định phong phú hơn và tham khảo dữ liệu phù hợp với từng quốc gia.

Nếu bổ sung thuế, trợ cấp hay chế độ hưu trí, cần kiểm tra văn bản pháp luật chính thức, ngày áp dụng và ngoại lệ. **Đây mới là định hướng, không phải tính năng đã có hoặc cam kết phát hành.**

### Vì sao một số nội dung chưa được tính?

Thuế theo hoàn cảnh cá nhân, trợ cấp xã hội, định giá bất động sản, nhiều nhóm tài sản đầu tư, nhiều loại tiền tệ và lương hưu theo quy định đều cần dữ liệu và giả định bổ sung. Không có một khoản mục trong mô hình **không có nghĩa** giá trị thực tế của nó bằng không.

Trong một số trường hợp, bạn có thể tự khai tác động đã biết dưới dạng **khoản tiền một lần** hoặc **thay đổi thu nhập hay chi tiêu hằng tháng**. Cần nêu rõ đây là ước tính tự nhập, không phải kết quả tính toán chính thức. Không nên xem chức năng dự kiến trong tương lai như chức năng đã có.

## 8. Nguyên tắc thiết kế

Công cụ ưu tiên giả định minh bạch, phân biệt dữ liệu quan sát với dự báo và tách biệt giá trị đang chỉnh sửa với kết quả đã tính.

Những thay đổi quan trọng cần được người dùng chủ động xác nhận. Hệ thống không tự suy đoán biến cố y tế, gia đình hoặc xã hội, cũng không tự gán xác suất cá nhân.

Mục tiêu là giúp người dùng đánh giá kết quả một cách có phê phán, thay vì xem một con số là sự thật tuyệt đối.

### Người dùng kiểm soát các giả định

Kịch bản cơ sở luôn được xác định rõ: những giá trị gợi ý không tự thay đổi tình hình tài chính của bạn. Việc tải một ví dụ có thể thay thế dữ liệu đang nhập sau khi bạn xác nhận; một sự kiện mẫu chỉ được thêm khi bạn chủ động chọn. **Giá trị minh họa** không phải **số liệu thống kê quan sát được**.

Để so sánh có ý nghĩa, hãy lưu một kịch bản ban đầu rồi tạo các bản khác, **mỗi bản thay đổi một yếu tố**: thời gian dự phóng, lợi suất, chi tiêu, con cái, thu nhập hoặc tuổi nghỉ hưu. Thay nhiều yếu tố cùng lúc khiến việc xác định nguyên nhân thay đổi kết quả khó hơn.

Số chữ số thập phân được hiển thị không đồng nghĩa với độ chính xác của dự báo kinh tế. Kết quả chỉ chính xác **trong khuôn khổ các giả định đã nhập**, không phải trong tương lai thực tế.

## 9. Sự kiện cuộc sống và trải nghiệm

Một sự kiện có thể là chuyển nhà, gián đoạn thu nhập, chi phí y tế hoặc mua sắm lớn. Người dùng chọn thời điểm bắt đầu, thời lượng, chi phí ban đầu và biến động thu nhập hay chi tiêu hằng tháng.

Mọi sự kiện đều có thể chỉnh sửa và không đi kèm xác suất cá nhân tự động. Cần tránh tính trùng khoản chi vốn đã nằm trong ngân sách cơ sở.

Các trường thiết yếu được ưu tiên; những giả định chuyên sâu được đặt ở khu vực riêng.

### Chi phí một lần và sự kiện kéo dài

Một khoản thu hoặc chi một lần chỉ xuất hiện ở tháng đã chọn, chẳng hạn mua thiết bị giá 2.000 € tại tháng 12. Một **sự kiện cuộc sống** có thể gồm chi phí ban đầu, chi tiêu bổ sung hằng tháng và thay đổi thu nhập trong một khoảng thời gian.

**Ví dụ giả định:** chuyển nhà bắt đầu tháng 7, kéo dài hai tháng, tốn 1.500 € lúc đầu và phát sinh thêm 200 € chi tiêu mỗi tháng. Tổng tác động trực tiếp là 1.900 € trước ảnh hưởng của lợi suất và lạm phát. Nếu tiền thuê mới đã nằm trong chi tiêu cơ sở, không được cộng thêm 200 € lần nữa.

Thu nhập giảm được khai bằng **mức thay đổi âm**; chi phí ban đầu và chi tiêu bổ sung được nhập là số dương. Tháng bắt đầu được tính trong thời lượng và toàn bộ sự kiện phải nằm trong thời gian dự phóng.

Những tình huống gợi ý như mất việc tạm thời, chi phí y tế, mua sắm lớn, trông trẻ, trợ giúp người thân và chuyển nhà đều là **ví dụ giả định, có thể sửa**, được xây dựng theo quy mô ngân sách của bạn. Chúng không phải chi phí trung bình quốc gia hay xác suất cá nhân.

## 10. Những yếu tố tài chính, xã hội và rủi ro

Tăng trưởng thu nhập, lạm phát, lợi suất đầu tư, tín dụng, hỗ trợ người thân và các biến cố nghề nghiệp hoặc sức khỏe có thể ảnh hưởng đến kết quả.

Ứng dụng phân biệt **phân tích độ nhạy**, **kịch bản bất lợi do người dùng chọn** và **mô phỏng xác suất đơn giản cho đầu tư**. Những công cụ này không cung cấp xác suất cá nhân bị thất nghiệp, mắc bệnh hoặc gặp biến cố.

Các tương quan kinh tế và tình huống cá nhân mới được phản ánh một phần.

### Ba cách phân tích sự bất định

**Phân tích độ nhạy:** so sánh lợi suất đầu tư giả định ở mức cơ sở với một mức thấp và một mức cao. Chênh lệch hai **điểm phần trăm** có thể là so sánh 5% với 3% và 7% mỗi năm. Không có xác suất riêng cho từng trường hợp.

**Kiểm tra sức chịu đựng:** áp dụng **một biến cố bất lợi mỗi lần** (mất thu nhập tạm thời, chi phí lớn, hỗ trợ người thân...) lên kịch bản cơ sở. Xem cả thay đổi tài sản cuối kỳ **lẫn** tiền mặt thấp nhất. Những biến cố này không được cộng dồn với nhau hay tự thêm vào kịch bản hiện tại.

**Monte Carlo:** lợi suất đầu tư theo tháng thay đổi ngẫu nhiên quanh giá trị trung bình và độ biến động giả định. Các phân vị **P10, P50, P90** biểu diễn **phân bố mô phỏng của tài sản ròng danh nghĩa** tại từng thời điểm. Ví dụ, P10 là ngưỡng mà 10% số đường mô phỏng nằm dưới đó vào thời điểm đang xét. Đây không phải ngưỡng bảo đảm hay dự báo cho cá nhân.

Lợi suất theo tháng được giả định độc lập với nhau, theo phân bố đơn giản có giới hạn mức lỗ mỗi tháng gần 99%. Thu nhập, chi tiêu, nợ, lợi tức tiền mặt và lạm phát vẫn cố định theo giả định. **Lưu ý:** tỷ lệ đường mô phỏng có tiền mặt âm vì vậy có thể là 0% hoặc 100%; đây không phải xác suất khủng hoảng thanh khoản được hiệu chỉnh từ dữ liệu thực.

Mô hình không tự gán xác suất mắc bệnh, thất nghiệp, gặp tai nạn hay biến cố gia đình.

## 11. Đánh giá và kiểm chứng

Quá trình bảo đảm chất lượng bao gồm kiểm tra tự động về tính nhất quán toán học, dữ liệu, điều hướng và giao diện đa ngôn ngữ.

Những kiểm tra đó không thay thế đánh giá độc lập với người dùng thật, nhà kinh tế, chuyên gia thuế hoặc chuyên gia tính toán bảo hiểm. **Không được xem như đã hoàn tất kiểm chứng bên ngoài.**

Kết luận của mô hình chỉ có giá trị tham khảo với các giả định đã chọn.

### Những điều đã kiểm tra và chưa thể khẳng định

Các bước kiểm tra tính nhất quán có thể phát hiện giá trị nhập sai, lịch trả nợ bất hợp lý, chuyển tiền nội bộ không nhất quán hoặc lỗi hiển thị. Chúng giúp giảm sai sót hiển nhiên, nhưng **không chứng minh rằng giả định của bạn thực tế hoặc kết quả sẽ xảy ra**.

Một đánh giá đầy đủ cần thêm phản hồi của người dùng thực, đối chiếu với các trường hợp thực tế có tài liệu và thẩm định độc lập của chuyên gia tài chính cùng quy tắc từng quốc gia. Ứng dụng **không tuyên bố** đã có xác nhận độc lập như vậy.

Nếu thấy kết quả bất thường, trước hết hãy kiểm tra tiền tệ, năm bắt đầu, thời gian dự phóng, chi phí đã nằm trong ngân sách gốc, thời điểm sự kiện và lần tính toán gần nhất.

## 12. Vòng đời và ngân sách gia đình

Hồ sơ cho **trẻ em**, **người lớn** và **người phụ thuộc khác** cho phép mô tả thay đổi chi tiêu và thu nhập theo thời gian.

Chi phí cho trẻ có thể thay đổi theo độ tuổi và thời gian hỗ trợ. Khi người lớn nghỉ hưu, thu nhập có thể thay đổi theo **mức lương hưu giả định**. Khoản giúp đỡ người thân được nhập riêng.

Tùy chọn **đã bao gồm trong chi tiêu hiện tại** giúp tránh tính trùng chi phí cơ sở. Các mức tiền đề xuất chỉ là ví dụ minh họa, không phải số trung bình toàn quốc. Nếu thời gian mô phỏng ngắn hơn thời gian hỗ trợ, kết quả chỉ bao gồm một phần chi phí.

### Trẻ em: tách riêng các loại chi phí

Đối với mỗi trẻ, phân biệt **chi phí sinh hoạt** với **chăm sóc hoặc giáo dục**, theo năm nhóm tuổi: **0–2, 3–5, 6–11, 12–17 và 18–29 tuổi**. Bạn chọn độ tuổi ban đầu, thời điểm bắt đầu chăm sóc và tuổi kết thúc hỗ trợ (tối đa 30 tuổi). Đây là nhóm phục vụ mô phỏng, **không phải định mức chi phí chính thức**.

**Ví dụ giả định:** một trẻ đang sống trong hộ có 350 € chi phí mỗi tháng **đã nằm trong** tổng chi tiêu 2.000 €. Nếu nhóm tuổi tiếp theo cần 450 €, phần chi tăng được tính là **chênh lệch 100 €** (chưa kể giả định tăng chi tiêu), chứ không cộng toàn bộ 450 € lần nữa. Với trẻ dự kiến sinh trong tương lai, chi phí chỉ bắt đầu từ thời điểm được chọn và không thể đã nằm trong chi tiêu hiện tại.

### Người lớn và nghỉ hưu giả định

Có thể phân bổ tối đa **100% thu nhập ròng của hộ** cho các người lớn được khai. Mỗi người có tuổi hiện tại, phần thu nhập, tuổi nghỉ hưu, tỷ lệ **giả định** giữa lương hưu và lương trước nghỉ hưu, cùng chi phí theo bốn nhóm tuổi: 18–39, 40–59, 60–74 và từ 75 tuổi. Người đã nghỉ hưu được xem là đang nhận mức lương hưu hiện tại, nên không áp dụng tỷ lệ thay thế thêm lần nữa. Sau khi nghỉ hưu trong mô phỏng, lương hưu tăng theo giả định lạm phát, không dựa trên quy định chính thức.

### Người phụ thuộc khác và các lưu ý

Việc hỗ trợ cha mẹ hoặc người thân khác có thể bao gồm tiền trợ giúp và chi phí chăm sóc theo tháng, với thời điểm bắt đầu và thời lượng. Nếu khoản hỗ trợ đã nằm trong chi tiêu cơ sở, hãy đánh dấu để chỉ tính **phần thay đổi**; khi hết thời gian hỗ trợ, chi phí cơ sở tương ứng có thể giảm.

Kiểm tra tổng các khoản “đã bao gồm” không vượt chi tiêu cơ sở. Mô hình không tự suy ra trợ cấp xã hội, chi phí y tế theo tuổi hoặc thời điểm qua đời. Nếu thời gian dự phóng kết thúc trước khi hết hỗ trợ, tổng chi phí chỉ bao gồm **thời gian đã mô phỏng**. Các khoản đề xuất là số liệu giả định.

