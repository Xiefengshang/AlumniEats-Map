import json
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType
from pyecharts.datasets import COORDINATES

# 1. 模板常量：HTML 结构保持不变，仅在 head 中引入新的网络字体
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>蹭饭图</title>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@4.1.0/map/js/china.js"></script>
  <style>
    {css}
  </style>
</head>
<body>
  <div class="main-container">
    <div class="header" id="chart-header"></div>
    <div class="grid-wrapper">
      <div class="info-column" id="left-column">{left_blocks}</div>
      <div class="map-wrapper"><div id="pyecharts-map"></div></div>
      <div class="info-column" id="right-column">{right_blocks}</div>
    </div>
    <svg class="svg-overlay" id="svg-layer"></svg>
  </div>
  <script>
    const cityGeoCoords = {geo_coords};
    const chartOptions   = {chart_options};
    document.addEventListener('DOMContentLoaded', () => {{
      const chartDom = document.getElementById('pyecharts-map');
      const myChart  = echarts.init(chartDom);
      
      chartOptions.tooltip.formatter = params => {{
        const d = params.data && params.data.cityData;
        if (!d) return '';
        let html = `<strong>${{params.name}}</strong> (${{d.students.length}}人)<br/>`;
        d.students.forEach(s => html += `${{s.name}} - ${{s.university}}<br/>`);
        return html;
      }};
      
      const titleOpt = chartOptions.title[0] || {{}};
      document.getElementById('chart-header').innerHTML =
        `<h1>${{titleOpt.text||''}}</h1><p>${{titleOpt.subtext||''}}</p>`;
      chartOptions.title[0].show = false;
      
      myChart.setOption(chartOptions);
      
      const svg   = document.getElementById('svg-layer');
      const wrap  = document.querySelector('.main-container');
      const draw  = () => {{
        svg.innerHTML = '';
        const cRect = wrap.getBoundingClientRect();
        for (let name in cityGeoCoords) {{
          const info = cityGeoCoords[name];
          const block= document.getElementById(`city-${{name.replace(/ /g,'_')}}`);
          if (!block) continue;
          const bRect = block.getBoundingClientRect();
          const start = {{
            x: (info.align === 'left' ? bRect.right  : bRect.left)  - cRect.left,
            y: (bRect.top + bRect.height/2) - cRect.top
          }};
          const [px, py] = myChart.convertToPixel('geo', info.coord) || [];
          const mRect     = chartDom.getBoundingClientRect();
          const end = {{ x: mRect.left - cRect.left + px, y: mRect.top - cRect.top + py }};
          const path = document.createElementNS('http://www.w3.org/2000/svg','path');
          const c1 = {{ x: start.x + (end.x - start.x)/2, y: start.y }};
          const c2 = {{ x: start.x + (end.x - start.x)/2, y: end.y }};
          path.setAttribute('d', `M${{start.x}} ${{start.y}} C ${{c1.x}} ${{c1.y}}, ${{c2.x}} ${{c2.y}}, ${{end.x}} ${{end.y}}`);
          
          // --- 优化点：修改线条样式 ---
          path.setAttribute('stroke','#4f5b6e'); // 更柔和的线条颜色
          path.setAttribute('stroke-width','1.5');
          path.setAttribute('stroke-dasharray', '5, 5'); // 改为虚线
          path.setAttribute('fill','none'); 
          path.setAttribute('opacity','0.8');
          
          svg.appendChild(path);
        }}
      }};
      myChart.on('finished', draw);
      myChart.on('georoam',   draw);
      new ResizeObserver(() => {{ myChart.resize(); draw(); }}).observe(wrap);
      window.addEventListener('scroll', draw, true);
    }});
  </script>
</body>
</html>
"""

# 2. 优化的 CSS
CSS_IMPROVED = """
:root {
  /* 浅色主题色系 */
  --bg-color: #f4f6f8;         /* 页面背景 */
  --container-bg: #ffffff;     /* 主容器背景 */
  --card-bg: #ffffff;          /* 卡片背景 */
  --primary-text: #343a40;     /* 主文本 */
  --secondary-text: #6c757d;   /* 次文本 */
  --accent-color: #17a2b8;     /* 强调色（青蓝）*/
  --border-color: #dee2e6;     /* 边框/分隔线 */
  --shadow-color: rgba(0,0,0,0.08);
}

body {
  font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--primary-text);
  margin: 0;
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.main-container {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 30px;
  background: var(--container-bg);
  border-radius: 12px;
  box-shadow: 0 4px 20px var(--shadow-color);
  position: relative;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}
.header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
  color: var(--primary-text);
}
.header p {
  margin: 6px 0 0;
  color: var(--secondary-text);
  font-size: 18px;
  font-weight: 300;
}

.grid-wrapper {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 30px;
  align-items: start;
}

.info-column {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-height: 700px;
  overflow-y: auto;
  padding-right: 8px;
}
/* 滚动条 */
.info-column::-webkit-scrollbar { width: 6px; }
.info-column::-webkit-scrollbar-track { background: transparent; }
.info-column::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
.info-column::-webkit-scrollbar-thumb:hover { background: var(--accent-color); }

.map-wrapper {
  position: relative;
  height: 700px;
}
#pyecharts-map {
  width: 100%;
  height: 100%;
}
.svg-overlay {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 5;
}

.city-block {
  padding: 14px 18px;
  background: var(--card-bg);
  border-left: 4px solid var(--accent-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--shadow-color);
  transition: transform .3s ease, box-shadow .3s ease;
}
.city-block:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px var(--shadow-color);
}
.city-block h3 {
  margin: 0 0 8px;
  color: var(--accent-color);
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 4px;
}
.city-block p {
  margin: 4px 0;
  color: var(--primary-text);
  font-size: 14px;
  line-height: 1.4;
}
"""

def generate_city_geo_data(data, division_long=114.0):
    """返回 {city_name: {'coord': [lng,lat], 'align':'left'/'right'}}"""
    out = {}
    for item in data:
        name = item['city_name']
        coord = COORDINATES.get(name)
        if coord:
            out[name] = {
                'coord': coord,
                'align': 'left'  if coord[0] <= division_long else 'right'
            }
        else:
            print(f"⚠️ 未找到城市[{name}]的坐标")
    return out

def build_info_blocks(data, geo_data, align_side):
    """生成 left 或 right 列的 HTML 块"""
    filtered = [
        d for d in data
        if geo_data.get(d['city_name'], {}).get('align') == align_side
    ]
    # 按纬度降序
    filtered.sort(key=lambda d: geo_data[d['city_name']]['coord'][1], reverse=True)
    blocks = []
    for d in filtered:
        sid = d['city_name'].replace(' ', '_')
        stu = "".join(f"<p>{s['name']} - {s['university']}</p>" for s in d['students'])
        blocks.append(f'<div class="city-block" id="city-{sid}">'
                      f'<h3>{d["city_name"]} ({len(d["students"])}人)</h3>{stu}</div>')
    return "\n".join(blocks)

def create_final_map(data, geo_data, output_file="graduates_map_final_v2.html"):
    # 1. 准备 Pyecharts 数据
    full_data = [
        {
            "name": city['city_name'],
            "value": [*geo_data[city['city_name']]['coord'], len(city['students'])],
            "cityData": city
        }
        for city in data
        if city['city_name'] in geo_data
    ]
    scatter_pairs = [(d['name'], d['value'][2]) for d in full_data]
    
    # --- 最终正确方案：使用 .set_series_opts() 设置样式 ---
    geo_chart = (
        Geo(init_opts=opts.InitOpts(
            chart_id="pyecharts-map",
            bg_color="transparent"
        ))
        .add_schema(
            maptype="china",
            zoom=1.2,
            itemstyle_opts=opts.ItemStyleOpts(
                color="#e9ecef",
                border_color="#dee2e6"
            ),
            # 地图区域的高亮样式在 add_schema 中设置是正确的
            emphasis_itemstyle_opts=opts.ItemStyleOpts(color="#17a2b8"),
            label_opts=opts.LabelOpts(is_show=False),
        )
        # 1. .add() 方法只负责添加数据，保持简洁
        .add(
            "毕业生去向", 
            scatter_pairs, 
            ChartType.SCATTER, 
            symbol_size=12,
        )
        # 2. 【关键修正】使用 .set_series_opts() 来设置所有关于系列的样式
        .set_series_opts(
            # 在这里设置高亮（emphasis）效果
            emphasis_opts=opts.EmphasisOpts(
                label_opts=opts.LabelOpts(is_show=False) # 悬停时，不显示系列标签
            )
        )
        # 3. 设置全局选项
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="可蹭饭根据地分布",
                subtitle="吃遍祖国大好河山🤤",
            ),
            visualmap_opts=opts.VisualMapOpts(
                is_show=True,
                type_="continuous",
                min_=min((d['value'][2] for d in full_data), default=0),
                max_=max((d['value'][2] for d in full_data), default=0),
                range_color=["#17a2b8", "#38d9a9", "#ff922b", "#f03e3e"],
                pos_left="5%",
                pos_bottom="5%",
                textstyle_opts=opts.TextStyleOpts(color="#343a40")
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                background_color="rgba(255,255,255,0.95)",
                border_width=1,
                border_color="#dee2e6",
                textstyle_opts=opts.TextStyleOpts(color="#343a40")
            ),
        )
    )
    # 覆盖 data，注入 cityData
    geo_chart.options['series'][0]['data'] = full_data
    chart_options_json = geo_chart.dump_options_with_quotes()

    # 生成左右两列 HTML
    left_html  = build_info_blocks(data, geo_data, 'left')
    right_html = build_info_blocks(data, geo_data, 'right')

    # 填充模板并写文件
    final_html = HTML_TEMPLATE.format(
        css=CSS_IMPROVED,
        chart_options=chart_options_json,
        geo_coords=json.dumps(geo_data, ensure_ascii=False),
        left_blocks=left_html,
        right_blocks=right_html
    )
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"✅ 成功生成优化版交互地图页面：{output_file}")

if __name__ == '__main__':
    sample_data = [
            {
                "city_name": "北京",
                "students": [
                    {
                        "name": "李宇航",
                        "university": "北京大学"
                    },
                    {
                        "name": "王梓睿",
                        "university": "清华大学"
                    },
                    {
                        "name": "张欣怡",
                        "university": "中国人民大学"
                    },
                    {
                        "name": "刘文轩",
                        "university": "北京师范大学"
                    },
                    {
                        "name": "陈俊杰",
                        "university": "北京航空航天大学"
                    },
                    {
                        "name": "杨一诺",
                        "university": "北京理工大学"
                    },
                    {
                        "name": "赵思睿",
                        "university": "中国农业大学"
                    },
                    {
                        "name": "黄皓宇",
                        "university": "中央财经大学"
                    },
                    {
                        "name": "周佳琪",
                        "university": "对外经济贸易大学"
                    },
                    {
                        "name": "吴雨泽",
                        "university": "中国政法大学"
                    }
                ]
            },
            {
                "city_name": "上海",
                "students": [
                    {
                        "name": "徐晨曦",
                        "university": "复旦大学"
                    },
                    {
                        "name": "孙梦洁",
                        "university": "上海交通大学"
                    },
                    {
                        "name": "胡静怡",
                        "university": "同济大学"
                    },
                    {
                        "name": "朱奕辰",
                        "university": "华东师范大学"
                    },
                    {
                        "name": "高子墨",
                        "university": "华东理工大学"
                    },
                    {
                        "name": "林晓晴",
                        "university": "上海外国语大学"
                    },
                    {
                        "name": "何沐宸",
                        "university": "上海财经大学"
                    },
                    {
                        "name": "郭梓萱",
                        "university": "东华大学"
                    },
                    {
                        "name": "马嘉豪",
                        "university": "上海大学"
                    }
                ]
            },
            {
                "city_name": "广州",
                "students": [
                    {
                        "name": "罗浩然",
                        "university": "中山大学"
                    },
                    {
                        "name": "梁诗涵",
                        "university": "华南理工大学"
                    },
                    {
                        "name": "宋子异",
                        "university": "暨南大学"
                    },
                    {
                        "name": "郑欣妍",
                        "university": "华南师范大学"
                    },
                    {
                        "name": "谢伊诺",
                        "university": "中山大学"
                    }
                ]
            },
            {
                "city_name": "南京",
                "students": [
                    {
                        "name": "韩俊宇",
                        "university": "南京大学"
                    },
                    {
                        "name": "唐乐萱",
                        "university": "东南大学"
                    },
                    {
                        "name": "冯一凡",
                        "university": "南京航空航天大学"
                    },
                    {
                        "name": "于文昊",
                        "university": "南京理工大学"
                    },
                    {
                        "name": "董佳怡",
                        "university": "河海大学"
                    },
                    {
                        "name": "程梓琳",
                        "university": "南京大学"
                    }
                ]
            },
            {
                "city_name": "武汉",
                "students": [
                    {
                        "name": "曹宇辰",
                        "university": "武汉大学"
                    },
                    {
                        "name": "袁明轩",
                        "university": "华中科技大学"
                    },
                    {
                        "name": "邓思远",
                        "university": "武汉理工大学"
                    },
                    {
                        "name": "许沐阳",
                        "university": "中国地质大学（武汉）"
                    },
                    {
                        "name": "傅浩",
                        "university": "华中师范大学"
                    },
                    {
                        "name": "沈一鸣",
                        "university": "中南财经政法大学"
                    },
                    {
                        "name": "曾子涵",
                        "university": "武汉大学"
                    }
                ]
            },
            {
                "city_name": "西安",
                "students": [
                    {
                        "name": "彭博文",
                        "university": "西安交通大学"
                    },
                    {
                        "name": "吕俊熙",
                        "university": "西北工业大学"
                    },
                    {
                        "name": "苏子轩",
                        "university": "西安电子科技大学"
                    },
                    {
                        "name": "卢皓轩",
                        "university": "长安大学"
                    },
                    {
                        "name": "蒋语桐",
                        "university": "西北大学"
                    },
                    {
                        "name": "蔡可馨",
                        "university": "陕西师范大学"
                    }
                ]
            },
            {
                "city_name": "成都",
                "students": [
                    {
                        "name": "贾瑞",
                        "university": "四川大学"
                    },
                    {
                        "name": "丁娜",
                        "university": "电子科技大学"
                    },
                    {
                        "name": "魏敏",
                        "university": "西南交通大学"
                    },
                    {
                        "name": "薛伟",
                        "university": "西南财经大学"
                    },
                    {
                        "name": "叶磊",
                        "university": "四川大学"
                    }
                ]
            },
            {
                "city_name": "杭州",
                "students": [
                    {
                        "name": "阎强",
                        "university": "浙江大学"
                    },
                    {
                        "name": "余洋",
                        "university": "浙江大学"
                    },
                    {
                        "name": "潘军",
                        "university": "浙江大学"
                    }
                ]
            },
            {
                "city_name": "天津",
                "students": [
                    {
                        "name": "杜明",
                        "university": "南开大学"
                    },
                    {
                        "name": "戴涛",
                        "university": "天津大学"
                    },
                    {
                        "name": "夏娟",
                        "university": "南开大学"
                    },
                    {
                        "name": "钟平",
                        "university": "天津医科大学"
                    }
                ]
            },
            {
                "city_name": "长沙",
                "students": [
                    {
                        "name": "汪丽",
                        "university": "中南大学"
                    },
                    {
                        "name": "田静",
                        "university": "湖南大学"
                    },
                    {
                        "name": "任秀英",
                        "university": "湖南师范大学"
                    },
                    {
                        "name": "姜芳",
                        "university": "国防科技大学"
                    }
                ]
            },
            {
                "city_name": "哈尔滨",
                "students": [
                    {
                        "name": "范欣怡",
                        "university": "哈尔滨工业大学"
                    },
                    {
                        "name": "方宇轩",
                        "university": "哈尔滨工程大学"
                    },
                    {
                        "name": "石浩宇",
                        "university": "东北林业大学"
                    },
                    {
                        "name": "姚梓涵",
                        "university": "哈尔滨工业大学"
                    }
                ]
            },
            {
                "city_name": "合肥",
                "students": [
                    {
                        "name": "谭晨曦",
                        "university": "中国科学技术大学"
                    },
                    {
                        "name": "廖俊杰",
                        "university": "合肥工业大学"
                    },
                    {
                        "name": "邹文轩",
                        "university": "安徽大学"
                    },
                    {
                        "name": "熊梓睿",
                        "university": "中国科学技术大学"
                    }
                ]
            },
            {
                "city_name": "大连",
                "students": [
                    {
                        "name": "金诗涵",
                        "university": "大连理工大学"
                    },
                    {
                        "name": "陆梦洁",
                        "university": "大连海事大学"
                    },
                    {
                        "name": "郝佳琪",
                        "university": "东北财经大学"
                    }
                ]
            },
            {
                "city_name": "厦门",
                "students": [
                    {
                        "name": "孔雨泽",
                        "university": "厦门大学"
                    },
                    {
                        "name": "白梓萱",
                        "university": "厦门大学"
                    }
                ]
            },
            {
                "city_name": "济南",
                "students": [
                    {
                        "name": "崔皓宇",
                        "university": "山东大学"
                    },
                    {
                        "name": "康欣妍",
                        "university": "山东大学"
                    }
                ]
            },
            {
                "city_name": "重庆",
                "students": [
                    {
                        "name": "毛俊熙",
                        "university": "重庆大学"
                    },
                    {
                        "name": "邱一诺",
                        "university": "西南大学"
                    },
                    {
                        "name": "秦思睿",
                        "university": "西南政法大学"
                    }
                ]
            },
            {
                "city_name": "青岛",
                "students": [
                    {
                        "name": "江浩然",
                        "university": "中国海洋大学"
                    },
                    {
                        "name": "史宇航",
                        "university": "中国石油大学（华东）"
                    }
                ]
            },
            {
                "city_name": "兰州",
                "students": [
                    {
                        "name": "顾佳怡",
                        "university": "兰州大学"
                    },
                    {
                        "name": "侯奕辰",
                        "university": "兰州大学"
                    }
                ]
            },
            {
                "city_name": "沈阳",
                "students": [
                    {
                        "name": "邵子墨",
                        "university": "东北大学"
                    },
                    {
                        "name": "孟晓晴",
                        "university": "辽宁大学"
                    }
                ]
            },
            {
                "city_name": "长春",
                "students": [
                    {
                        "name": "龙沐宸",
                        "university": "吉林大学"
                    },
                    {
                        "name": "万子异",
                        "university": "东北师范大学"
                    },
                    {
                        "name": "段嘉豪",
                        "university": "吉林大学"
                    }
                ]
            },
            {
                "city_name": "郑州",
                "students": [
                    {
                        "name": "雷文昊",
                        "university": "郑州大学"
                    },
                    {
                        "name": "钱乐萱",
                        "university": "郑州大学"
                    }
                ]
            },
            {
                "city_name": "深圳",
                "students": [
                    {
                        "name": "汤一凡",
                        "university": "南方科技大学"
                    },
                    {
                        "name": "尹梓琳",
                        "university": "深圳大学"
                    },
                    {
                        "name": "黎宇辰",
                        "university": "哈尔滨工业大学（深圳）"
                    }
                ]
            },
            {
                "city_name": "昆明",
                "students": [
                    {
                        "name": "易明轩",
                        "university": "云南大学"
                    }
                ]
            },
            {
                "city_name": "徐州",
                "students": [
                    {
                        "name": "常思远",
                        "university": "中国矿业大学"
                    }
                ]
            },
            {
                "city_name": "福州",
                "students": [
                    {
                        "name": "武沐阳",
                        "university": "福州大学"
                    }
                ]
            },
            {
                "city_name": "南昌",
                "students": [
                    {
                        "name": "乔浩",
                        "university": "南昌大学"
                    }
                ]
            },
            {
                "city_name": "太原",
                "students": [
                    {
                        "name": "贺一鸣",
                        "university": "太原理工大学"
                    },
                    {
                        "name": "赖子涵",
                        "university": "山西大学"
                    }
                ]
            }
        ]
    city_geo = generate_city_geo_data(sample_data)
    create_final_map(sample_data, city_geo)