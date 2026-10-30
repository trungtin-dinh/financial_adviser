# Hướng dẫn công khai — Financial Adviser

Tài liệu này giới thiệu mục đích, giả định toán học và giới hạn của công cụ mà không đi sâu vào chi tiết lập trình. Đây là nội dung giáo dục, không phải tư vấn tài chính cá nhân.

## 1. Mục tiêu và phạm vi

**Financial Adviser** giúp khảo sát thu nhập, chi tiêu, tiền mặt, đầu tư, nợ và mục tiêu tài sản của một hộ gia đình trong tương lai. Người dùng có thể thay đổi giả định, so sánh kịch bản và thêm những sự kiện trong cuộc sống.

Ứng dụng không phải hệ thống theo dõi ngân hàng thời gian thực hay công cụ dự báo chắc chắn cho từng cá nhân. Mỗi kịch bản chỉ dùng **một loại tiền tệ**; đổi giữa Pháp và Việt Nam không tự động quy đổi số tiền.

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

## 3. Nguồn dữ liệu và độ tin cậy

Ứng dụng phân biệt **thống kê quá khứ**, **giả định cho tương lai** và **quy định pháp luật**. Không nên trực tiếp sử dụng một con số trung bình toàn quốc để thay thế thu nhập hoặc chi phí của gia đình mình.

Các nguồn tham khảo chính gồm [Insee](https://www.insee.fr/fr/information/8184146), [Ngân hàng Trung ương Pháp](https://www.banque-france.fr/fr) và [Cục Thống kê Việt Nam](https://www.nso.gov.vn/en/).

Trang số liệu thống kê riêng biệt trình bày phạm vi, thời kỳ và nguồn của từng quan sát. Hệ thống hiện **không tự động tính thuế** theo luật quốc gia.

## 4. Nguyên tắc sử dụng

Quy trình chính gồm **nhập kế hoạch**, **điều chỉnh giả định**, **chạy mô phỏng** và **xem kết quả**.

Biểu đồ thể hiện tài sản ròng, tiền mặt, đầu tư và dư nợ. Các chỉ báo cho biết khả năng thiếu hụt tiền mặt và mức độ đạt được mục tiêu đã đặt ra. Có thể so sánh các giả định mà không tự động thay đổi kịch bản gốc.

Người dùng có thể chủ động nhập hoặc xuất kế hoạch dưới dạng JSON. Ứng dụng không tự lấy giao dịch từ ngân hàng.

## 5. So với những công cụ khác

Ứng dụng quản lý chi tiêu thường tập trung vào ngân sách hiện tại hoặc quá khứ; công cụ theo dõi danh mục tập trung vào đầu tư; công cụ lập kế hoạch khảo sát **những kịch bản tương lai có điều kiện**.

Financial Adviser tập trung vào loại thứ ba. Ứng dụng không thay thế phần mềm kế toán, dịch vụ khai thuế, tính lương hưu chính thức hoặc tư vấn đầu tư được cấp phép.

## 6. Giới hạn, chất lượng và quyền riêng tư

Mô hình chưa bao quát đầy đủ thuế, mọi loại phí sản phẩm, trợ cấp xã hội, tỷ giá và giá trị tài sản bất động sản chưa được khai báo.

**Tiền mặt âm** thể hiện khoản thiếu hụt chưa có nguồn tài trợ, không đồng nghĩa với việc ngân hàng chấp nhận thấu chi hay tài sản được bán tự động. Kết quả tốt không chứng minh kế hoạch chắc chắn khả thi.

Ứng dụng không yêu cầu kết nối ngân hàng. Dữ liệu nhập trên phiên bản trực tuyến vẫn được xử lý trên máy chủ trong thời gian sử dụng. Hãy dùng số liệu giả định hoặc chạy cục bộ nếu dữ liệu quá nhạy cảm.

## 7. Hướng phát triển có thể xem xét

Các hướng mở rộng gồm thêm loại tài sản và khoản nợ, mô hình hóa bất định phong phú hơn và tham khảo dữ liệu phù hợp với từng quốc gia.

Nếu bổ sung thuế, trợ cấp hay chế độ hưu trí, cần kiểm tra văn bản pháp luật chính thức, ngày áp dụng và ngoại lệ. **Đây mới là định hướng, không phải tính năng đã có hoặc cam kết phát hành.**

## 8. Nguyên tắc thiết kế

Công cụ ưu tiên giả định minh bạch, phân biệt dữ liệu quan sát với dự báo và tách biệt giá trị đang chỉnh sửa với kết quả đã tính.

Những thay đổi quan trọng cần được người dùng chủ động xác nhận. Hệ thống không tự suy đoán biến cố y tế, gia đình hoặc xã hội, cũng không tự gán xác suất cá nhân.

Mục tiêu là giúp người dùng đánh giá kết quả một cách có phê phán, thay vì xem một con số là sự thật tuyệt đối.

## 9. Sự kiện cuộc sống và trải nghiệm

Một sự kiện có thể là chuyển nhà, gián đoạn thu nhập, chi phí y tế hoặc mua sắm lớn. Người dùng chọn thời điểm bắt đầu, thời lượng, chi phí ban đầu và biến động thu nhập hay chi tiêu hằng tháng.

Mọi sự kiện đều có thể chỉnh sửa và không đi kèm xác suất cá nhân tự động. Cần tránh tính trùng khoản chi vốn đã nằm trong ngân sách cơ sở.

Các trường thiết yếu được ưu tiên; những giả định chuyên sâu được đặt ở khu vực riêng.

## 10. Những yếu tố tài chính, xã hội và rủi ro

Tăng trưởng thu nhập, lạm phát, lợi suất đầu tư, tín dụng, hỗ trợ người thân và các biến cố nghề nghiệp hoặc sức khỏe có thể ảnh hưởng đến kết quả.

Ứng dụng phân biệt **phân tích độ nhạy**, **kịch bản bất lợi do người dùng chọn** và **mô phỏng xác suất đơn giản cho đầu tư**. Những công cụ này không cung cấp xác suất cá nhân bị thất nghiệp, mắc bệnh hoặc gặp biến cố.

Các tương quan kinh tế và tình huống cá nhân mới được phản ánh một phần.

## 11. Đánh giá và kiểm chứng

Quá trình bảo đảm chất lượng bao gồm kiểm tra tự động về tính nhất quán toán học, dữ liệu, điều hướng và giao diện đa ngôn ngữ.

Những kiểm tra đó không thay thế đánh giá độc lập với người dùng thật, nhà kinh tế, chuyên gia thuế hoặc chuyên gia tính toán bảo hiểm. **Không được xem như đã hoàn tất kiểm chứng bên ngoài.**

Kết luận của mô hình chỉ có giá trị tham khảo với các giả định đã chọn.

## 12. Vòng đời và ngân sách gia đình

Hồ sơ cho **trẻ em**, **người lớn** và **người phụ thuộc khác** cho phép mô tả thay đổi chi tiêu và thu nhập theo thời gian.

Chi phí cho trẻ có thể thay đổi theo độ tuổi và thời gian hỗ trợ. Khi người lớn nghỉ hưu, thu nhập có thể thay đổi theo **mức lương hưu giả định**. Khoản giúp đỡ người thân được nhập riêng.

Tùy chọn **đã bao gồm trong chi tiêu hiện tại** giúp tránh tính trùng chi phí cơ sở. Các mức tiền đề xuất chỉ là ví dụ minh họa, không phải số trung bình toàn quốc. Nếu thời gian mô phỏng ngắn hơn thời gian hỗ trợ, kết quả chỉ bao gồm một phần chi phí.
