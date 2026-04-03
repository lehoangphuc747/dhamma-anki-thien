# -*- coding: utf-8 -*-
"""
Cập nhật trường `explain` trong:
    Dhamma_Anki_by_topic_json/all_topics.json

Map theo `id` dạng: "Dhamma - 0001" .. "Dhamma - 0012".

Chạy từ thư mục Thiền:
    python scripts/update_explain_by_id.py
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
JSON_PATH = BASE / "Dhamma_Anki_by_topic_json" / "all_topics.json"

EXPLAIN_UPDATES: dict[str, str] = {
    "Dhamma - 0001": "Hơi thở (Ana/Apana). Trong thiền định, hơi thở là đối tượng quán niệm thuần khiết nhất. Nó là cây cầu nối tự nhiên giữa ý thức và vô thức, giữa thân (Rupa) và tâm (Nama). Hành giả chỉ quan sát hơi thở tự nhiên như nó đang là, không điều khiển, từ đó phát triển chánh niệm (Sati) và định tâm (Samadhi).",
    "Dhamma - 0002": "Sự hô hấp. Thuật ngữ này nhấn mạnh vào quá trình động và liên tục của việc thở ra và hít vào. Sự quan sát 'respiration' một cách sắc bén giúp hành giả nhận diện nhịp điệu tự nhiên của sự sống, đặt nền tảng ban đầu để thấu hiểu luật Vô thường (Anicca) ngay trong từng khoảnh khắc sinh diệt của luồng hơi.",
    "Dhamma - 0003": "Hơi thở ra (Apana). Một nửa của vòng tuần hoàn Anapana. Khi luồng hơi đi ra, hành giả ghi nhận 'đang thở ra' với sự tỉnh giác trọn vẹn (Sampajanna). Không cố ý kéo dài hay làm ngắn lại, chỉ đơn thuần nhận biết sự cọ xát của không khí tại cửa mũi hoặc trên môi trên, thiết lập sự chánh niệm tại một điểm duy nhất.",
    "Dhamma - 0004": "Hơi thở vào (Ana). Hành giả ghi nhận rõ ràng sự bắt đầu, đoạn giữa và sự kết thúc của một luồng hơi thở đi vào. Sự chú tâm vào luồng không khí mát mẻ đi vào mũi giúp gom tâm lại, thu hẹp vùng không gian quan sát để làm tâm trở nên nhạy bén, vi tế và tập trung hơn.",
    "Dhamma - 0005": "Hơi thở vi tế. Khi tâm dần trở nên an tịnh và bớt xáo động (Samatha), hơi thở tự nhiên sẽ ngắn lại, trở nên vô cùng nhẹ nhàng và mỏng manh. Đôi lúc hành giả có cảm giác như hơi thở đã ngừng lại. Đây là dấu hiệu định lực đang tăng trưởng, đòi hỏi sự chú ý (Attention) cực kỳ sắc bén để tiếp tục duy trì sự nhận biết.",
    "Dhamma - 0006": "Hơi thở thuần túy như nó đang là (Yathabhuta). Nguyên tắc cốt lõi của thiền Anapana là tuyệt đối không can thiệp hay điều khí (Pranayama). Việc chấp nhận hoàn toàn hơi thở tự nhiên—dù thô hay tế, sâu hay nông—giúp huấn luyện tâm xả ly (Upekkha), không phản ứng với thực tại và triệt tiêu thói quen kiểm soát của bản ngã.",
    "Dhamma - 0007": "Hơi thở có chủ đích. Thường chỉ được áp dụng như một phương tiện chữa cháy tạm thời (vài nhịp) khi tâm quá trạo cử, hôn trầm hoặc trôi dạt vào dòng suy nghĩ miên man. Bằng cách thở hơi mạnh và có ý thức, hành giả mỏ neo tâm trở lại hiện tại trước khi lập tức quay về với sự quan sát hơi thở tự nhiên.",
    "Dhamma - 0008": "Hơi thở thô tháo. Thường xuất hiện tự nhiên khi tâm bị kích động bởi các chướng ngại (Nivarana) như sân hận, lo âu, hoặc cơ thể đang đau đớn. Hành giả chỉ cần khách quan ghi nhận 'đây là hơi thở mạnh' mà không phán xét hay cố làm dịu nó. Sự quan sát thuần túy này dần dần sẽ tự động xoa dịu cả tâm lẫn nhịp thở.",
    "Dhamma - 0009": "Trạng thái hô hấp bị nén hoặc cạn cợt do sự căng thẳng tâm lý (Tension) hoặc sự cố gắng quá sức để tập trung. Lời khuyên là hành giả cần lùi lại, buông bỏ sự khao khát (Craving) muốn đạt được trạng thái thiền sâu, thư giãn cơ thể và để cho hệ hô hấp tự vận hành nhịp điệu của riêng nó.",
    "Dhamma - 0010": "Thiết lập Chánh niệm (Sati) trên đối tượng. Đây không phải là suy nghĩ, tưởng tượng hay niệm thầm về hơi thở, mà là sự trải nghiệm trực tiếp sự xúc chạm vật lý của luồng hơi ngay tại vùng cửa mũi. Sự nhận biết liên tục, không đứt đoạn là mảnh đất màu mỡ để phát sinh trí tuệ thực chứng (Panna).",
    "Dhamma - 0011": "Một thao tác hoàn toàn bị cấm kỵ trong truyền thống Vipassana (trái ngược với Yoga Pranayama). Việc 'điều khiển' sẽ nuôi dưỡng sự bám chấp vào một cái tôi (Ngã) đang làm chủ và kiểm soát thực tại. Thiền tuệ đòi hỏi sự quan sát vô ngã (Anatta), để mọi thứ diễn ra theo đúng quy luật tự nhiên của chúng.",
    "Dhamma - 0012": "Cửa ngõ của hệ hô hấp và là vùng giới hạn không gian (Area of attention) để hành giả neo giữ tâm trí trong giai đoạn Anapana. Bằng cách thu hẹp phạm vi quan sát quanh lỗ mũi, tâm dần trở nên hội tụ, sắc bén như một mũi kim, chuẩn bị năng lực để thấu triệt những cảm thọ vi tế (Subtle sensations) trên toàn thân sau này.",
    "Dhamma - 0013": "Vùng cửa ngõ nơi luồng khí đi vào và đi ra. Trong giai đoạn thiền Anapana, hành giả thu hẹp sự chú ý tại khu vực nhỏ hẹp này để mài giũa sự tập trung. Diện tích quan sát càng nhỏ, tâm càng trở nên sắc bén và vi tế, chuẩn bị năng lực để nhận biết những cảm thọ cực kỳ mỏng manh.",
    "Dhamma - 0014": "Nơi diễn ra sự cọ xát đầu tiên của luồng hơi. Hành giả ghi nhận mọi cảm giác nảy sinh tại khu vực này (như sự ấm, mát, ngứa, nhột hay cọ xát) với sự tỉnh giác (Sampajanna) và giữ tâm khách quan tuyệt đối, không phản ứng thuận nghịch.",
    "Dhamma - 0015": "Khu vực rìa của cửa mũi, tiếp giáp với môi trên. Việc khoanh vùng chính xác điểm tiếp xúc của hơi thở tại đây giúp tâm không bị phân tán ra bên ngoài, từ đó phát triển Chánh định (Samma Samadhi) một cách vững chãi.",
    "Dhamma - 0016": "Đường dẫn luồng sinh khí. Việc quan sát sự di chuyển của không khí qua ống mũi giúp hành giả nhận diện rõ đặc tính thực sự của luồng hơi: thô hay tế, dài hay ngắn, qua đó kinh nghiệm trực tiếp sự thay đổi liên tục của sắc pháp (Rupa).",
    "Dhamma - 0017": "Hơi thở thuần khiết, không bị xen lẫn bởi các câu thần chú (Mantra), hình ảnh tưởng tượng hay khái niệm ngôn ngữ. Việc chỉ quan sát luồng không khí đi vào và đi ra giúp tâm đối diện trực tiếp với thực tại chân đế (Paramattha Sacca), không bị lạc vào ảo ảnh.",
    "Dhamma - 0018": "Sự quan sát đã được tước bỏ mọi khái niệm chế định (Pannatti). Hành giả không gán tên gọi 'đây là hơi thở', mà chỉ đơn thuần kinh nghiệm sự xúc chạm vật lý. Đây là bước đệm quan trọng để gọt rửa tâm trí khỏi những dính mắc vào khái niệm.",
    "Dhamma - 0019": "Tầng tâm thức nông cạn, nơi các suy nghĩ, logic, ký ức và ngôn ngữ hoạt động mạnh mẽ. Thiền Vipassana yêu cầu hành giả không dừng lại ở lớp bề mặt đầy xáo động này, mà phải dùng định lực xuyên thấu xuống cội rễ của tâm, nơi các phản ứng vi tế thực sự diễn ra.",
    "Dhamma - 0020": "Trạng thái tiếp nhận thực tại chỉ qua lăng kính của trí tuệ vay mượn từ người khác (Suta-maya panna) hoặc trí tuệ tự suy luận logic (Cinta-maya panna), chưa chạm đến cốt lõi của sự giải thoát là thực chứng tuệ (Bhavana-maya panna).",
    "Dhamma - 0021": "Sự hiểu biết giáo pháp qua sách vở và tư duy trí óc. Dù cần thiết làm bản đồ chỉ đường ban đầu, nhưng sự dính mắc ở mức độ trí năng là một chướng ngại lớn. Trí năng không đủ sức mạnh để nhổ tận gốc rễ của những ô nhiễm (Kilesa) nằm sâu dưới các tầng vô thức.",
    "Dhamma - 0022": "Trí tuệ phát sinh nhờ kinh nghiệm trực tiếp trên thân (Bhavana-maya panna). Khi hành giả tự mình trải nghiệm tính Vô thường (Anicca) thông qua sự sinh diệt của cảm thọ, đó mới là sự giác ngộ thực sự, mang lại năng lực tịnh hóa nội tâm và giải thoát khỏi khổ đau.",
    "Dhamma - 0023": "Phần tâm trí bề mặt (Vinnana) nhận biết thông tin từ sáu căn (Mắt, Tai, Mũi, Lưỡi, Thân, Ý). Dù nó có thể đang niệm 'vô thường, vô ngã', nhưng nếu tầng vô thức vẫn mù quáng phản ứng bằng tham và sân, tâm trí vẫn chưa thực sự được thanh lọc.",
    "Dhamma - 0024": "Tầng sâu thẳm của tâm, hoạt động liên tục ngày đêm không ngừng nghỉ. Đây là kho chứa của các Hành (Sankhara) - những phản ứng và thói quen ngầm sâu kín. Thực hành Vipassana chính là cuộc phẫu thuật tâm linh vào tầng tiềm thức này, dùng lưỡi dao Chánh niệm để cắt đứt các gốc rễ ô nhiễm.",
    "Dhamma - 0025": "Tầng vô thức (Anusaya). Nơi ngấm ngầm lưu trữ các tập khí (Sankhara) từ vô thủy. Dù bề mặt tâm có thể đang ngủ hay đang bận rộn tư duy, vô thức vẫn liên tục đo lường và phản ứng với các cảm thọ trên thân bằng tham và sân. Vipassana rọi ánh sáng Chánh niệm vào vùng tối này để đánh thức sự tỉnh giác.",
    "Dhamma - 0026": "Ô nhiễm (Kilesa). Các yếu tố bất thiện làm vẩn đục tâm trí, ngăn cản trí tuệ sáng suốt. Trong hành thiền, defilement thường trồi lên bề mặt dưới dạng các chướng ngại (Nivarana) như trạo cử hay hôn trầm. Hành giả cần giữ tâm xả ly, chỉ quan sát sự sinh diệt của chúng để gọt rửa nội tâm.",
    "Dhamma - 0027": "Bất tịnh (Asava). Những cặn bã tâm linh, các lậu hoặc sinh ra từ vô minh và những phản ứng mù quáng trong quá khứ. Phương pháp Vipassana là một quá trình thanh lọc (Purification) liên tục, dùng ngọn lửa của sự nhận biết thuần túy để thiêu rụi các hạt giống bất tịnh này từ tận gốc rễ.",
    "Dhamma - 0028": "Tiêu cực (Akusala). Bất kỳ trạng thái tâm nào thiếu vắng sự bình an, điển hình là giận dữ, sợ hãi, ghen tị hay phiền não. Khi negativity nổi lên, hành giả không đè nén cũng không biểu đạt ra ngoài (suppression/expression), mà chỉ quay lại quan sát cảm thọ đi kèm trên thân để nó tự sinh và diệt.",
    "Dhamma - 0029": "Tâm tham (Lobha/Tanha). Cội rễ của luân hồi và khổ đau. Là sự thèm khát, bám víu mãnh liệt vào các cảm thọ dễ chịu (Pleasant sensations) sinh ra trên thân. Hành giả Vipassana rèn luyện để khi cảm thọ hỷ lạc xuất hiện, chỉ ghi nhận tính vô thường của nó mà không sinh khởi tâm tham đắm.",
    "Dhamma - 0030": "Tâm sân (Dosa). Phản ứng đẩy ra, chối bỏ, kháng cự đối với các cảm thọ khó chịu (Unpleasant sensations) như đau nhức, tê mỏi. Việc giữ tâm quân bình (Equanimity), mỉm cười chấp nhận cơn đau bức bách mà không nhúc nhích chính là cách hiệu quả nhất để nhổ rễ tâm sân hận.",
    "Dhamma - 0031": "Vô minh (Avijja). Sự mù lòa về bản chất thực sự của vạn pháp (Vô thường, Khổ, Vô ngã). Là nguyên nhân sâu xa nhất khiến tâm liên tục phản ứng tạo nghiệp mới. Ánh sáng của tuệ giác (Panna) sinh ra từ việc trực tiếp quan sát cảm thọ sẽ xua tan bóng tối vô minh này.",
    "Dhamma - 0032": "Ảo tưởng (Maya). Sự đánh lừa của tâm trí, nhìn nhận một khối danh sắc (Nama-Rupa) luôn sinh diệt là một cái 'Tôi' (Ngã) thường hằng, hoặc thấy cái khổ là vui, cái bất tịnh là thanh tịnh. Thực hành thiền tuệ là phá vỡ ảo tưởng biểu kiến để chạm đến sự thật chân đế.",
    "Dhamma - 0033": "Mê lầm (Moha). Trạng thái tâm si mê, mất tỉnh giác, đánh mất sự nhận biết trong phút giây hiện tại. Trạng thái này khiến hành giả dễ trôi lăn trong các dòng suy nghĩ miên man vô ý thức, quên mất nhiệm vụ duy trì sự quan sát khách quan các cảm thọ trên thân.",
    "Dhamma - 0034": "Dính mắc (Upadana). Trạng thái tâm bị trói buộc vào đối tượng do sức kéo của tâm tham (Craving). Trong hành thiền, chướng ngại lớn nhất thường là sự dính mắc vào những trải nghiệm thiền tốt đẹp (ánh sáng, sự tĩnh lặng, cảm giác rỗng rang vô trọng lượng), làm cản trở tiến trình đi sâu hơn.",
    "Dhamma - 0035": "Bám víu. Mức độ thô tháo, bám chặt và mãnh liệt hơn của attachment. Khi hành giả bám víu vào một trạng thái thiền sâu trong quá khứ và khởi lên sự khao khát nó phải lặp lại, họ đã tự tạo ra một rào cản nội tâm mới, đánh mất đi thực tại vô thường của khoảnh khắc hiện tiền.",
    "Dhamma - 0036": "Thế giới bên trong (Ajjhatta). Toàn bộ vũ trụ của danh và sắc (Mind and Matter) nằm gọn trong khuôn khổ cơ thể dài khoảng một sải tay này. Hành giả Vipassana không tìm kiếm chân lý ở thế giới bên ngoài, mà quay vào trong khám phá toàn bộ quy luật tự nhiên của vũ trụ thông qua chính tấm thân này.",
    "Dhamma - 0037": "Khuôn mẫu thói quen (Sankhara). Phản xạ có điều kiện của tâm trí được lặp đi lặp lại nhiều đời. Khi gặp cảm thọ dễ chịu, thói quen là sinh tham; gặp khó chịu, thói quen là sinh sân. Vipassana bẻ gãy khuôn mẫu mù quáng này bằng cách chêm 'sự tỉnh giác' và 'tâm xả' vào giữa sự xuất hiện của cảm thọ và sự phản ứng.",
    "Dhamma - 0038": "Trôi lăn trong suy nghĩ (Papanca). Trạng thái tâm phóng dật, liên tục nhân bản các ý niệm, quá khứ, tương lai tạo thành một dòng thác vọng tưởng. Khi phát hiện tâm đang trôi lăn, hành giả chỉ mỉm cười ghi nhận thực tại đó và nhẹ nhàng đưa tâm về lại với hơi thở hoặc cảm thọ hiện tại, tuyệt đối không tự trách móc.",
    "Dhamma - 0039": "Tâm xả (Upekkha). Một trong bốn Phạm trú (Brahma-vihara) và là mục tiêu cốt lõi của thiền Vipassana. Không phải là sự thờ ơ hay trơ lì vô cảm, mà là trạng thái tâm thăng bằng tuyệt đối. Do thấu triệt luật vô thường (Anicca), tâm không phản ứng (non-reaction) bằng tham hay sân trước bất kỳ cảm thọ thô hay tế nào.",
    "Dhamma - 0040": "Trạng thái giữ sự thăng bằng tâm trí. Hành giả thực hành 'be equanimous' bằng cách đóng vai trò một nhân chứng khách quan (objective observer). Bất kể điều gì xảy ra trên thân hay trong tâm, chỉ đơn thuần ghi nhận sự thật tự nhiên: 'Nó đang là như vậy, và rồi nó cũng sẽ thay đổi'.",
    "Dhamma - 0041": "Duy trì tâm xả liên tục. Sự thử thách lớn nhất không phải là đạt được tâm xả trong chốc lát, mà là duy trì nó (remain) trước những cơn bão của cảm thọ cường liệt (đau đớn tột cùng hoặc hỷ lạc ngập tràn). Duy trì sự bình thản là thước đo thực sự cho sự vững chãi trên đạo lộ giải thoát.",
    "Dhamma - 0042": "Tâm thanh tịnh (Visuddhi). Trạng thái tâm đã được gọt rửa khỏi các ô nhiễm (Kilesa) thô tháo và vi tế. Trong khoảnh khắc tâm hoàn toàn xả ly, không có một mảy may tham hay sân xen vào, đó là một khoảnh khắc của tâm thanh tịnh. Sự tích lũy những khoảnh khắc này sẽ dẫn đến sự tịnh hóa nội tâm hoàn toàn.",
    "Dhamma - 0043": "Tâm dao động (Uddhacca). Trạng thái tâm không an trú được trên đối tượng, bị khuấy động bởi phiền não, hoài nghi hoặc sự mong cầu kết quả. Khi tâm xáo động mạnh, hành giả được khuyên nên quay lại với đối tượng thô hơn là hơi thở (Anapana) thay vì cố quét cảm thọ vi tế, để tâm dần lắng dịu và quy nhất trở lại.",
    "Dhamma - 0044": "Tâm an tĩnh (Samatha). Kết quả của việc tâm tập trung liên tục vào một đối tượng duy nhất (như hơi thở). Tuy nhiên, trong Vipassana, sự yên lặng này chỉ là công cụ (Định) để dọn đường cho trí tuệ (Tuệ) phát sinh, để quan sát các vi hạt cấu tạo nên thân thể, chứ không phải là đích đến cuối cùng để đắm chìm và dính mắc.",
    "Dhamma - 0045": "Tâm tỉnh giác (Sampajanna) và chánh niệm (Sati). Tâm không bị rơi vào hôn trầm (thờ thẫn, buồn ngủ), luôn giữ được sự nhạy bén và chú tâm liên tục vào sự sinh diệt của các cảm thọ. Sự chăm chú sắc bén này hoạt động như mũi dao phẫu thuật, bóc tách và cắt đứt các khối vô minh ngầm sâu trong vô thức.",
    "Dhamma - 0046": "Trạng thái lý tưởng của hành giả Vipassana. Sự kết hợp hoàn hảo giữa năng lực định tâm vững vàng và trí tuệ vô thường. Tâm như một chiếc cân thăng bằng tuyệt đối, không nghiêng lệch về phía khao khát (khi gặp lạc thọ) hay ghét bỏ (khi gặp khổ thọ), chỉ thuần túy quan sát mọi hiện tượng đến rồi đi.",
    "Dhamma - 0047": "Tâm phóng tâm, không bám trụ ở hiện tại (Monkey mind). Bản chất tự nhiên của tâm chưa được huấn luyện là luôn nhảy từ nhánh cây quá khứ sang tương lai. Khi nhận ra tâm đang đi lang thang, khoảnh khắc nhận ra đó chính là lúc Chánh niệm đã quay về, hành giả hoan hỷ đưa nó lại với đề mục thiền mà không sinh tâm sân hận.",
    "Dhamma - 0048": "Trạng thái tâm (Citta). Một trong bốn nền tảng của Tứ niệm xứ (Cittanupassana - Quán tâm). Hành giả quan sát tâm như một khách thể: tâm đang có tham biết là có tham, tâm đang phân tán biết là phân tán. Quan sát một cách khách quan mà không đồng hóa 'tôi đang tức giận' hay 'tôi đang buồn'.",
}


def main() -> None:
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {JSON_PATH}")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("all_topics.json không phải mảng (list).")

    by_id: dict[str, dict] = {}
    for item in data:
        if isinstance(item, dict) and "id" in item:
            by_id[str(item["id"])] = item

    missing: list[str] = []
    updated = 0
    for idv, expl in EXPLAIN_UPDATES.items():
        if idv in by_id:
            by_id[idv]["explain"] = expl
            updated += 1
        else:
            missing.append(idv)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak_path = JSON_PATH.with_name(f"all_topics.json.bak_explain_{ts}")
    bak_path.write_text(JSON_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated explain: {updated}/{len(EXPLAIN_UPDATES)}")
    if missing:
        print("Missing ids:", missing)


if __name__ == "__main__":
    main()

