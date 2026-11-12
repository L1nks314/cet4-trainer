# -*- coding: utf-8 -*-
"""翻译采分点数据：每句 2-4 个必译信息点，各给可接受写法（alt 用 | 分隔）。

写完后跑 scripts/check_trans_pts.py 自检：每个 alt 必须能在参考译文里命中，
否则说明这套写法学生照抄参考译文都判不出来。
"""
import json
import os

PUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# key: 套号，value: 按句序的点表 [[中文标签, "写法1|写法2"], ...]
D = {
 "2022-06-1": [
  [["从前", "once upon a time"], ["禾苗", "rice seedlings"], ["长得慢", "growing too slowly"], ["一株株", "one by one"], ["拔高", "pulled them up"]],
  [["回家后", "after returning home"], ["累坏了", "worn out"], ["总算", "finally"], ["一下子", "all at once"]],
  [["儿子", "his son"], ["到地里", "went to the field"], ["死光了", "withered"]],
  [["如今", "nowadays"], ["急于让孩子成功", "eager to see their children succeed"], ["步后尘", "follow in the farmer"], ["学业长进", "progress in their studies"]],
  [["醒悟", "wake up to this problem"], ["自然成长", "grow naturally"]],
 ],
 "2022-12-1": [
  [["农历", "lunar calendar"], ["立秋", "start of autumn"], ["意味着", "marks the end of summer"], ["秋天的开始", "beginning of autumn"]],
  [["首先", "first brings"], ["天气变化", "change in the weather"], ["气温下降", "gradually drop"]],
  [["变黄飘落", "turn yellow and fall"], ["秋天已经来临", "autumn has arrived"], ["一叶知秋", "one falling leaf"]],
  [["并未完全结束", "not completely ended"], ["持续一段时间", "continue for a while"], ["秋老虎", "autumn tiger"]],
  [["意义重大", "great significance to farmers"], ["迅速生长", "grow rapidly"], ["收获季节", "harvest season is approaching"]],
 ],
 "2022-12-2": [
  [["农历", "lunar calendar"], ["春天的开始", "beginning of spring"], ["表示", "marks"]],
  [["白天变长", "days grow longer"], ["天气温暖", "weather becomes warmer"], ["万物复苏", "comes back to life"], ["充满生机", "full of vitality"]],
  [["一年之计在于春", "depends on a good start in spring"], ["播种", "start sowing"], ["打下基础", "lay the foundation"], ["丰收", "good harvest"]],
  [["三千年前", "3,000 years ago"], ["举行庆祝活动", "hold celebrations"], ["早在", "as early as"]],
  [["数百年来", "for centuries"], ["迎春", "welcoming spring"], ["民间习俗", "folk custom"]],
  [["春暖花开", "in full bloom"], ["外出游玩", "go out for outings"], ["春天的美景", "beautiful scenery"]],
 ],
 "2023-06-1": [
  [["越来越重视", "increasing importance"], ["终身教育", "lifelong education"], ["继续教育", "continuing education"], ["有效途径", "effective way"]],
  [["人才培养的基地", "base for cultivating talent"], ["教学理念", "teaching philosophies"], ["教学资源", "teaching resources"], ["办学主体", "main providers"]],
  [["适应社会需求", "adapting to social needs"], ["用人单位", "employers"], ["中国国情", "national conditions"], ["发挥更大作用", "play a greater role"]],
 ],
 "2023-06-2": [
  [["改革开放", "reform and opening-up"], ["越来越重视", "increasing importance"], ["高等教育", "higher education"], ["稳步发展", "steady development"]],
  [["高校学生总数", "total number of college students"], ["接近4700万", "nearly 47 million"], ["位居世界第一", "ranking first"]],
  [["快速发展", "rapid development"], ["生活水平", "living standards"], ["越来越多的人", "more and more people"], ["渴望", "eager to receive"]],
  [["高校数量", "colleges and universities"], ["学科专业", "disciplines"], ["招生人数", "enrollment rises year by year"], ["教学质量", "teaching quality"]],
 ],
 "2023-06-3": [
  [["义务教育", "compulsory education"], ["大力推行", "vigorously promoting"], ["享有受教育的机会", "access to education"]],
  [["生效", "came into effect"], ["不懈努力", "unremitting efforts"], ["全国推行", "available nationwide"]],
  [["六周岁", "at the age of six"], ["小学", "primary school"], ["九年", "nine years"], ["初中", "junior high school"]],
  [["秋季学期", "autumn semester"], ["无须缴纳", "no longer had to pay"], ["学费", "tuition fees"]],
  [["一系列改革举措", "educational reform measures"], ["实施", "implementation"], ["显著提高", "improved significantly"]],
 ],
 "2023-12-1": [
  [["十分重视", "great importance"], ["健康饮食", "healthy diet"]],
  [["大力提倡", "vigorous promotion"], ["合理营养", "balanced nutrition"], ["增进健康", "improving health"]],
  [["基本需要", "basic need"], ["美好生活", "better life"], ["幸福感", "sense of happiness"], ["食品产业", "food industry"]],
  [["各级政府", "governments at all levels"], ["多种举措", "various measures"], ["健康中国", "healthy china"]],
 ],
 "2023-12-2": [
  [["显著变化", "significant changes"], ["饮食", "diet"]],
  [["经济落后", "backward economy"], ["种类有限", "limited in variety"], ["数量不足", "insufficient in quantity"], ["吃得饱", "enough to eat"]],
  [["丰富多样", "abundant and diverse"], ["质量提高", "improved in quality"], ["不仅", "not only"]],
  [["生活水平", "living standards"], ["要求越来越高", "higher demands"], ["营养健康", "nutritious and healthy"]],
  [["低脂", "low-fat"], ["低糖", "low-sugar"], ["有机食品", "organic food"], ["普遍欢迎", "widely welcomed"]],
 ],
 "2023-12-3": [
  [["生活水平", "living standards"], ["不断提高", "improved steadily"], ["充分体现", "fully reflected"], ["饮食变化", "changes in people"]],
  [["不再满足", "no longer content"], ["追求", "pursue"], ["丰富多样", "more and more diverse"], ["本地农产品", "local agricultural products"]],
  [["物流业", "logistics industry"], ["特产", "specialties"], ["全国各地", "all over the country"]],
  [["饮食结构", "diet structure"], ["有力保障", "strong guarantee"], ["增进健康", "improving people"]],
 ],
 "2024-06-1": [
  [["传统住宅建筑", "traditional chinese residential building"], ["特点", "characterized by"], ["四周", "four sides of a courtyard"], ["合围", "enclosing it"]],
  [["冬暖夏凉", "warm in winter and cool in summer"], ["环境舒适", "comfortable environment"], ["大家庭", "large families"]],
  [["多种类型", "various types"], ["最为典型", "most typical"], ["北京", "beijing"]],
  [["逐渐减少", "gradually decreased"], ["独特建筑风格", "unique architectural style"], ["文化传承", "inheritance of chinese culture"], ["历史研究", "study of chinese history"]],
 ],
 "2024-06-2": [
  [["起源", "originated"], ["数千年前", "thousands of years ago"], ["运行规律", "movements of the sun"]],
  [["重要作用", "important role"], ["农业生产", "agricultural production"], ["日常生活", "daily life"]],
  [["记录日期", "recorded dates"], ["安排农活", "arranged farm work"], ["自然资源", "natural resources"], ["产量和质量", "yield and quality"]],
  [["传统节日", "traditional festivals"], ["春节", "spring festival"], ["中秋节", "mid-autumn festival"], ["基于", "based on"]],
  [["重要组成部分", "important part"], ["传统文化", "traditional chinese culture"], ["广为使用", "widely used"]],
 ],
 "2024-06-3": [
  [["福", "character"], ["幸福和好运", "happiness and good fortune"], ["吉祥符号", "auspicious symbols"], ["传统文化", "traditional chinese culture"]],
  [["红纸", "red paper"], ["家庭幸福", "family happiness"], ["社会安定", "social stability"], ["国家昌盛", "national prosperity"]],
  [["贴福字", "pasting the character"], ["由来已久", "long-standing"], ["习俗", "folk custom"]],
  [["家家户户", "every household"], ["门上或墙上", "doors or walls"], ["向往", "longing for a happy life"], ["美好未来", "better future"]],
  [["倒过来", "upside down"], ["已到", "have arrived"]],
 ],
 "2024-12-1": [
  [["十分重视", "great importance"], ["环境保护", "environmental protection"]],
  [["显著成效", "remarkable progress"], ["减少污染", "reducing air"], ["土壤", "soil"]],
  [["一系列有效措施", "series of effective measures"], ["清洁能源", "clean energy"], ["公共交通", "public transportation"], ["垃圾分类", "garbage classification"]],
  [["城市和农村", "urban and rural areas"], ["绿起来", "becoming greener"]],
  [["国际合作", "international cooperation"], ["重要贡献", "important contributions"], ["全球环境保护", "global environmental protection"]],
 ],
 "2024-12-2": [
  [["新能源汽车", "new energy vehicle"], ["发展迅速", "developed rapidly"]],
  [["年产量", "annual output"], ["近千万辆", "nearly 10 million"], ["市场份额", "global market share"], ["出口量", "exports"], ["新高", "new highs"]],
  [["资金投入", "increasing funding"], ["政策引导", "policy guidance"], ["技术创新", "technological innovations"], ["竞争力", "competitiveness"]],
  [["国内经济", "domestic economic growth"], ["新能源利用", "use of new energy"], ["环境保护", "environmental protection"]],
 ],
 "2024-12-3": [
  [["2014年开放", "opened in 2014"], ["重要组成部分", "important part"], ["保护利用", "protection and utilization"]],
  [["数字技术", "digital technology"], ["多媒体", "multimedia"], ["历史文化", "history and culture"], ["艺术经典", "artistic classics"]],
  [["减少洞窟数量", "reduce the number"], ["缩短逗留时间", "shorten the time"], ["减轻影响", "lessen the impact"], ["世界文化遗产", "world cultural heritage"], ["妥善保护", "properly protected"]],
 ],
 "2025-06-1": [
  [["杂交水稻之父", "father of hybrid rice"], ["科研团队", "research team"], ["重重困难", "numerous difficulties"], ["研发", "developed"]],
  [["巨大成功", "great success"], ["举世公认", "recognized worldwide"]],
  [["抗旱抗病", "resistance to drought"], ["适应", "adapt to"], ["气候和土壤", "climates and soil"], ["产量", "yield"]],
  [["营养丰富", "rich in nutrition"], ["口感更佳", "tastes better"]],
  [["广泛应用", "widely applied"], ["重大贡献", "great contributions"], ["粮食安全", "food security"]],
 ],
 "2025-06-2": [
  [["东北地区", "northeast china"], ["冰雪资源", "ice and snow resources"], ["大力开发", "vigorously developing"]],
  [["哈尔滨", "harbin"], ["冰雪大世界", "ice and snow world"], ["地方特色", "local characteristics"], ["民俗文化", "folk culture"], ["冰雪之美", "beauty of ice and snow"]],
  [["曾经令人畏惧", "once-feared"], ["四面八方", "from all directions"], ["旅游胜地", "tourist destination"]],
  [["冰雪旅游业", "ice and snow tourism"], ["越来越大", "increasingly great"], ["经济发展", "economic development"]],
 ],
 "2025-12-1": [
  [["中国政府", "chinese government"], ["高度重视", "great importance"], ["民营经济", "private economy"], ["一系列政策", "series of policies"], ["支持民营企业", "support private enterprises"]],
  [["截至", "by the end of"], ["超过", "exceeded"], ["5700万", "57 million"], ["占企业总量", "accounting for"]],
  [["不仅", "not only"], ["稳步增长", "growing steadily"], ["质量和结构", "quality and structure"]],
  [["研发投入", "investment"], ["新一代信息技术", "next-generation information technology"], ["人工智能", "artificial intelligence"], ["发展迅速", "developing rapidly"]],
  [["核心竞争力", "core competitiveness"], ["高质量发展", "high-quality development"], ["有力支撑", "strong support"]],
 ],
}


def js_dump():
    lines = ['/* 翻译采分点：每句 2-4 个必译信息点，alt 用 | 分隔（小写、按前缀匹配）。',
             '   生成脚本 scripts/gen_trans_pts.py，改数据请改那边再重跑。 */',
             'window.CET4_TRANS = {']
    for sid in sorted(D):
        lines.append('"%s": [' % sid)
        for sent in D[sid]:
            pts = ','.join('["%s","%s"]' % (z.replace('"', '\\"'), a.replace('"', '\\"')) for z, a in sent)
            lines.append('  [%s],' % pts)
        lines.append('],')
    lines.append('};')
    return '\n'.join(lines)


if __name__ == '__main__':
    p = os.path.join(PUB, 'explain', 'trans.js')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(js_dump())
    n = sum(len(v) for v in D.values())
    m = sum(len(s) for v in D.values() for s in v)
    print('sets', len(D), 'sentences', n, 'points', m, '->', p)
