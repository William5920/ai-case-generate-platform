import json
import io
import uuid
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from app.models.db_models import SplitRequirement, TestPoint, TestCase, Requirement


class XMindService:
    """XMind 导入导出服务"""

    XMIND_NS = "urn:xmind:xmap:xmlns:content:2.0"
    FO_NS = "http://www.w3.org/1999/XSL/Format"

    async def export_test_points(
        self, db: AsyncSession, requirement_id: str
    ) -> bytes:
        """导出测试点为 XMind 文件"""
        # 查询需求
        req_result = await db.execute(
            select(Requirement).where(Requirement.id == requirement_id)
        )
        requirement = req_result.scalar_one_or_none()
        if not requirement:
            raise ValueError("需求不存在")

        # 查询拆分需求和测试点
        result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .options(selectinload(SplitRequirement.test_points))
            .order_by(SplitRequirement.sort_order)
        )
        split_reqs = result.scalars().all()

        # 构建 content.xml
        xmap_content = self._build_content_xml(
            requirement_title=requirement.title,
            split_requirements=split_reqs,
        )

        # 构建 ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('content.xml', xmap_content)
            zf.writestr('metadata.xml', self._build_metadata_xml())
            zf.writestr('styles.xml', self._build_styles_xml())
            zf.writestr('META-INF/manifest.xml', self._build_manifest_xml())

        return zip_buffer.getvalue()

    def _build_content_xml(
        self, requirement_title: str, split_requirements: List[SplitRequirement]
    ) -> bytes:
        """构建 XMind content.xml（返回 UTF-8 bytes）"""
        # 注册命名空间，避免 ET 生成 ns0/ns1 前缀
        ET.register_namespace('', self.XMIND_NS)
        ET.register_namespace('fo', self.FO_NS)

        # 创建工作簿
        workbook = ET.Element(f'{{{self.XMIND_NS}}}xmap-content', {
            'version': '2.0',
        })

        # 第一个 sheet
        sheet = ET.SubElement(workbook, f'{{{self.XMIND_NS}}}sheet', {
            'id': self._gen_id(),
            'timestamp': '0',
        })
        sheet_title = ET.SubElement(sheet, f'{{{self.XMIND_NS}}}title')
        sheet_title.text = requirement_title

        # 中心主题（根需求）
        root_topic = ET.SubElement(sheet, f'{{{self.XMIND_NS}}}topic', {
            'id': self._gen_id(),
            'structure-class': 'org.xmind.ui.map.unbalanced',
            'timestamp': '0',
        })
        root_title = ET.SubElement(root_topic, f'{{{self.XMIND_NS}}}title')
        root_title.text = requirement_title

        children_elem = ET.SubElement(root_topic, f'{{{self.XMIND_NS}}}children')
        topics_elem = ET.SubElement(children_elem, f'{{{self.XMIND_NS}}}topics', {'type': 'attached'})

        # 拆分需求 —> 一级子主题
        for sr in split_requirements:
            sr_topic = ET.SubElement(topics_elem, f'{{{self.XMIND_NS}}}topic', {
                'id': self._gen_id(),
                'timestamp': '0',
            })
            sr_title = ET.SubElement(sr_topic, f'{{{self.XMIND_NS}}}title')
            sr_title.text = sr.text

            # 测试点 —> 二级子主题
            tp_list = sorted(sr.test_points, key=lambda tp: tp.created_at or 0)
            if tp_list:
                sr_children = ET.SubElement(sr_topic, f'{{{self.XMIND_NS}}}children')
                sr_topics = ET.SubElement(sr_children, f'{{{self.XMIND_NS}}}topics', {'type': 'attached'})
                for tp in tp_list:
                    # topic id 中嵌入 db_id 作为备份：gen-xxx--db-TP_DB_ID
                    tp_topic_id = self._gen_id()
                    if tp.id:
                        tp_topic_id = f'{tp_topic_id}--db-{tp.id}'

                    tp_topic = ET.SubElement(sr_topics, f'{{{self.XMIND_NS}}}topic', {
                        'id': tp_topic_id,
                        'timestamp': '0',
                    })
                    tp_title = ET.SubElement(tp_topic, f'{{{self.XMIND_NS}}}title')
                    tp_title.text = tp.text

                    # 将数据库 ID 写入 notes（用于导入时匹配）
                    if tp.id:
                        notes_elem = ET.SubElement(tp_topic, f'{{{self.XMIND_NS}}}notes')
                        plain_notes = ET.SubElement(notes_elem, f'{{{self.XMIND_NS}}}plain')
                        meta = {"db_id": tp.id, "description": tp.description or ""}
                        plain_notes.text = json.dumps(meta, ensure_ascii=False)

        xml_bytes = ET.tostring(workbook, encoding='utf-8')
        return b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + xml_bytes

    def _build_manifest_xml(self) -> bytes:
        """构建 META-INF/manifest.xml"""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
  <file-entry full-path="META-INF/" media-type=""/>
  <file-entry full-path="metadata.xml" media-type="text/xml"/>
  <file-entry full-path="styles.xml" media-type="text/xml"/>
</manifest>'''.encode('utf-8')

    def _build_metadata_xml(self) -> bytes:
        """构建 metadata.xml"""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">
  <Author>
    <Name>AI Case Platform</Name>
  </Author>
  <Create>
    <Time>{}</Time>
  </Create>
  <Creator>
    <Name>AI Case Platform</Name>
    <Version>1.0</Version>
  </Creator>
</meta>'''.format(datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')).encode('utf-8')

    def _build_styles_xml(self) -> bytes:
        """构建 styles.xml（空模板，满足 XMind 桌面端格式校验）"""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" version="2.0">
  <styles>
    <style id="default" type="topic">
      <topic-properties/>
    </style>
  </styles>
  <master-styles/>
</xmap-styles>'''.encode('utf-8')

    async def parse_xmind(self, file_content: bytes) -> dict:
        """解析 XMind 文件，返回结构化的测试点数据。

        自动识别两种格式：
        - 旧版 XMind 8（content.xml，XML 格式）
        - 新版 XMind 2020+（content.json，JSON 格式）

        注意：新版 XMind 文件中虽然也会包含 content.xml，但通常只是一个占位的
        多语言提示（"你可以尝试使用 XMind 8 Update 3 或更新版本打开"），并非真实
        数据，因此检测到 content.json 时必须优先使用，否则会把提示文案当成测试点。
        """
        zip_buffer = io.BytesIO(file_content)
        try:
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                names = set(zf.namelist())
                # 优先按新版 JSON 解析（XMind 2020/2022/2023 默认格式）
                if 'content.json' in names:
                    content_json = zf.read('content.json')
                    parsed = self._parse_xmind_json_content(content_json)
                    # 仅当 JSON 中确实解析到内容（拆分需求或测试点）时才采用，
                    # 避免遇到只有空 JSON 的文件时回退到占位 XML 误判。
                    if self._has_real_content(parsed):
                        return parsed
                # 旧版或回退：使用 content.xml
                if 'content.xml' in names:
                    content_xml = zf.read('content.xml')
                    parsed = self._parse_xmind_xml_content(content_xml)
                    # 检测到占位警告（说明其实是新版文件，但 content.json 缺失/为空）
                    if self._is_placeholder_warning(parsed):
                        raise ValueError(
                            "该 XMind 文件为新版格式，但未找到可解析的 content.json，"
                            "请使用 XMind 8 Update 3 或更新版本重新保存后重试。"
                        )
                    return parsed
                raise ValueError("XMind 文件中未找到 content.xml 或 content.json")
        except zipfile.BadZipFile:
            raise ValueError("无效的 XMind 文件")
        except KeyError:
            raise ValueError("XMind 文件中未找到 content.xml 或 content.json")

    # 占位警告文案关键词（多语言版本中都包含 "XMind 8 Update 3" 字样）
    _PLACEHOLDER_KEYWORDS = ("XMind 8 Update 3", "xmind 8 update 3")

    def _is_placeholder_warning(self, parsed: dict) -> bool:
        """检测 content.xml 是否仅为新版 XMind 的占位警告。

        新版 XMind 在保存时，content.xml 通常只包含一个根主题和若干语言版本的
        "你可以尝试使用 XMind 8 Update 3 或更新版本打开" 提示，没有真实数据。
        """
        split_reqs = parsed.get("split_requirements") or []
        # 所有测试点文本都命中关键词才认为是占位警告
        tp_texts = []
        for sr in split_reqs:
            for tp in sr.get("test_points") or []:
                if tp.get("text"):
                    tp_texts.append(tp["text"])
        if not tp_texts:
            return False
        for text in tp_texts:
            if not any(kw.lower() in (text or "").lower() for kw in self._PLACEHOLDER_KEYWORDS):
                return False
        return True

    def _has_real_content(self, parsed: dict) -> bool:
        """判断解析结果是否包含真实的拆分需求或测试点。"""
        for sr in parsed.get("split_requirements") or []:
            if sr.get("test_points"):
                return True
            if sr.get("text"):
                return True
        return False

    def _parse_xmind_xml_content(self, content_xml: bytes) -> dict:
        """解析旧版 XMind 8 的 content.xml 格式"""
        root = ET.fromstring(content_xml)
        ns = self.XMIND_NS

        def _find(elem, tag):
            """查找命名空间元素，同时兼容无命名空间的情况"""
            result = elem.find(f'{{{ns}}}{tag}')
            if result is None:
                result = elem.find(tag)
            return result

        def _findall(elem, tag):
            """查找所有命名空间元素，同时兼容无命名空间的情况"""
            results = elem.findall(f'{{{ns}}}{tag}')
            if not results:
                results = elem.findall(tag)
            return results

        # 查找 type="attached" 的 topics（跳过 summary/boundary/detached 等）
        def _find_attached_topics(elem):
            children = _find(elem, 'children')
            if children is None:
                return None
            # 查找 type="attached" 的 topics
            all_topics_list = _findall(children, 'topics')
            for t in all_topics_list:
                if t.get('type') == 'attached':
                    return t
            # fallback：返回第一个 topics
            if all_topics_list:
                return all_topics_list[0]
            return None

        # 提取 topic id 中嵌入的 db_id：格式 gen-xxx--db-TP_DB_ID
        def _extract_db_id_from_topic_id(topic_id):
            if topic_id and '--db-' in topic_id:
                return topic_id.split('--db-')[-1]
            return None

        # 从 notes 元素中提取文本（兼容 plain 和 html 两种格式）
        def _extract_notes_text(notes_elem):
            plain_elem = _find(notes_elem, 'plain')
            if plain_elem is not None and plain_elem.text:
                return plain_elem.text
            html_elem = _find(notes_elem, 'html')
            if html_elem is not None:
                # html notes 中包含 xhtml:p 等元素，取所有文本拼接
                texts = []
                for p in html_elem.iter():
                    if p.text:
                        texts.append(p.text)
                text = ''.join(texts).strip()
                if text:
                    return text
            return None

        # 提取元数据 JSON（从 notes 文本或 topic id）
        def _extract_meta(tp_topic):
            db_id = None
            description = ""
            notes_elem = _find(tp_topic, 'notes')
            if notes_elem is not None:
                notes_text = _extract_notes_text(notes_elem)
                if notes_text:
                    try:
                        meta = json.loads(notes_text)
                        db_id = meta.get("db_id")
                        description = meta.get("description", "")
                    except (json.JSONDecodeError, AttributeError):
                        pass
            # 从 topic id 属性中提取 db_id（fallback）
            if not db_id:
                tp_topic_id = tp_topic.get('id', '')
                db_id = _extract_db_id_from_topic_id(tp_topic_id)
            return db_id, description

        # 查找 sheet
        sheets = root.findall(f'{{{ns}}}sheet') or root.findall('sheet')
        if not sheets:
            return {"split_requirements": []}

        sheet = sheets[0]
        # 找到根 topic（sheet 下第一个 topic 就是根主题）
        root_topic = _find(sheet, 'topic')
        if root_topic is None:
            return {"split_requirements": []}

        # 一级子主题 = 拆分需求（root topic 下 attached topics）
        topics_elem = _find_attached_topics(root_topic)
        if topics_elem is None:
            return {"split_requirements": []}

        split_requirements = []
        for sr_topic in _findall(topics_elem, 'topic'):
            sr_title_elem = _find(sr_topic, 'title')
            sr_text = sr_title_elem.text or "" if sr_title_elem is not None else ""

            # 二级子主题 = 测试点
            test_points = []
            sr_topics = _find_attached_topics(sr_topic)
            if sr_topics is not None:
                for tp_topic in _findall(sr_topics, 'topic'):
                    tp_title_elem = _find(tp_topic, 'title')
                    tp_text = tp_title_elem.text or "" if tp_title_elem is not None else ""
                    db_id, description = _extract_meta(tp_topic)
                    test_points.append({
                        "db_id": db_id,
                        "text": tp_text,
                        "description": description,
                    })

            split_requirements.append({
                "text": sr_text,
                "test_points": test_points,
            })

        return {"split_requirements": split_requirements}

    def _parse_xmind_json_content(self, content_json: bytes) -> dict:
        """解析新版 XMind 2020+ 的 content.json 格式。

        content.json 的顶层是 sheet 数组，每个 sheet 包含 rootTopic；
        rootTopic 的一级 attached 子主题视为拆分需求，二级视为测试点。
        notes.plain.content 中存储平台写入的元数据 JSON（db_id/description）。
        """
        try:
            data = json.loads(content_json.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"解析 content.json 失败: {e}")

        if not isinstance(data, list) or not data:
            return {"split_requirements": []}

        sheet = data[0]
        if not isinstance(sheet, dict):
            return {"split_requirements": []}

        root_topic = sheet.get("rootTopic") or {}
        root_attached = (root_topic.get("children") or {}).get("attached") or []

        split_requirements = []
        for sr_topic in root_attached:
            if not isinstance(sr_topic, dict):
                continue
            sr_text = sr_topic.get("title", "") or ""

            sr_attached = (sr_topic.get("children") or {}).get("attached") or []
            test_points = []
            for tp_topic in sr_attached:
                if not isinstance(tp_topic, dict):
                    continue
                tp_text = tp_topic.get("title", "") or ""
                db_id, description = self._extract_meta_from_json_topic(tp_topic)
                test_points.append({
                    "db_id": db_id,
                    "text": tp_text,
                    "description": description,
                })

            split_requirements.append({
                "text": sr_text,
                "test_points": test_points,
            })

        return {"split_requirements": split_requirements}

    def _extract_meta_from_json_topic(self, tp_topic: dict):
        """从新版 JSON topic 中提取 db_id 和 description。

        优先从 notes.plain.content 解析平台写入的元数据 JSON，
        其次从 topic id（gen-xxx--db-TP_DB_ID）中回退提取。
        """
        db_id = None
        description = ""

        notes = tp_topic.get("notes")
        if isinstance(notes, dict):
            plain = notes.get("plain") or {}
            plain_content = plain.get("content")
            if plain_content:
                try:
                    meta = json.loads(plain_content)
                    if isinstance(meta, dict):
                        db_id = meta.get("db_id")
                        description = meta.get("description", "") or ""
                except (json.JSONDecodeError, AttributeError):
                    pass

        if not db_id:
            topic_id = tp_topic.get("id", "") or ""
            if "--db-" in topic_id:
                db_id = topic_id.split("--db-")[-1]

        return db_id, description

    def _match_split_requirements(
        self, parsed: dict, db_split_reqs: List[SplitRequirement]
    ) -> List[tuple]:
        """将解析出的拆分需求与数据库中的拆分需求匹配。

        返回 [(parsed_sr, matched_db_sr), ...]，未匹配的 parsed_sr 不在结果中。
        匹配规则：先按文本匹配，再按索引回退。

        preview 与 apply 必须使用同一套匹配逻辑，否则会出现
        "预览数据与导入数据对不上" 的问题：预览会统计所有 parsed 中的测试点，
        而 apply 只处理能匹配到拆分需求的测试点，导致两侧 added/updated/deleted 计数不一致。
        """
        db_sr_map = {sr.text: sr for sr in db_split_reqs}
        matched_pairs: List[tuple] = []
        sr_index = 0
        for sr in parsed.get("split_requirements", []):
            matched_sr = db_sr_map.get(sr.get("text", ""))
            if not matched_sr and sr_index < len(db_split_reqs):
                matched_sr = db_split_reqs[sr_index]
            if matched_sr:
                matched_pairs.append((sr, matched_sr))
            sr_index += 1
        return matched_pairs

    async def preview_import(
        self, db: AsyncSession, requirement_id: str, file_content: bytes
    ) -> dict:
        """预览导入变更。

        注意：此处必须使用与 apply_import 完全相同的拆分需求匹配逻辑，
        否则预览统计的 added/updated/deleted 数量会与实际导入结果不一致。
        """
        parsed = await self.parse_xmind(file_content)

        # 获取数据库中现有的测试点
        tp_result = await db.execute(
            select(TestPoint)
            .join(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        existing_tps = {tp.id: tp for tp in tp_result.scalars().all()}

        # 获取数据库中的拆分需求（按顺序）——与 apply 保持一致
        sr_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .order_by(SplitRequirement.sort_order)
        )
        db_split_reqs = sr_result.scalars().all()
        matched_pairs = self._match_split_requirements(parsed, db_split_reqs)

        # 仅收集能匹配到拆分需求的测试点（与 apply 行为一致）
        xmind_tp_ids = set()
        xmind_tp_items = []
        for sr, _matched in matched_pairs:
            for tp in sr["test_points"]:
                xmind_tp_items.append(tp)
                if tp["db_id"]:
                    xmind_tp_ids.add(tp["db_id"])

        added_items = []
        updated_items = []
        deleted_items = []
        conflict_ids = []
        marked_ignored_items = []

        for tp in xmind_tp_items:
            if tp["db_id"] and tp["db_id"] in existing_tps:
                existing = existing_tps[tp["db_id"]]
                if tp["text"] != existing.text or tp.get("description") != (existing.description or ""):
                    if existing.marked:
                        marked_ignored_items.append({
                            "id": tp["db_id"],
                            "oldText": existing.text,
                            "newText": tp["text"],
                        })
                    else:
                        updated_items.append({
                            "id": tp["db_id"],
                            "oldText": existing.text,
                            "newText": tp["text"],
                        })
            else:
                added_items.append({
                    "text": tp["text"],
                    "description": tp.get("description", ""),
                })

        # 数据库中有但 XMind 中没有的 = 待删除
        existing_ids = set(existing_tps.keys())
        for tp_id in existing_ids - xmind_tp_ids:
            tp = existing_tps[tp_id]
            case_count = await db.execute(
                select(func.count(TestCase.id)).where(TestCase.test_point_id == tp_id)
            )
            case_cnt = case_count.scalar() or 0
            deleted_items.append({
                "id": tp_id,
                "text": tp.text,
                "hasCases": case_cnt > 0,
            })
            if case_cnt > 0:
                conflict_ids.append(tp_id)

        return {
            "addedCount": len(added_items),
            "updatedCount": len(updated_items),
            "deletedCount": len(deleted_items),
            "markedIgnoredCount": len(marked_ignored_items),
            "addedItems": added_items,
            "updatedItems": updated_items,
            "deletedItems": deleted_items,
            "markedIgnoredItems": marked_ignored_items,
            "hasCasesConflict": len(conflict_ids) > 0,
            "conflictTestPointIds": conflict_ids,
        }

    async def apply_import(
        self, db: AsyncSession, requirement_id: str, file_content: bytes
    ) -> dict:
        """执行导入：全量同步测试点"""
        parsed = await self.parse_xmind(file_content)

        # 获取数据库现有测试点
        tp_result = await db.execute(
            select(TestPoint)
            .join(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
        )
        existing_tps = {tp.id: tp for tp in tp_result.scalars().all()}

        xmind_tp_ids = set()
        now = datetime.utcnow()
        added = 0
        updated = 0
        deleted = 0
        marked_ignored = 0

        # 获取数据库中的拆分需求（按顺序）
        sr_result = await db.execute(
            select(SplitRequirement)
            .where(SplitRequirement.requirement_id == requirement_id)
            .order_by(SplitRequirement.sort_order)
        )
        db_split_reqs = sr_result.scalars().all()
        # 使用与 preview 相同的匹配逻辑，保证两侧计数一致
        matched_pairs = self._match_split_requirements(parsed, db_split_reqs)

        for sr, matched_sr in matched_pairs:
            for tp in sr["test_points"]:
                if tp["db_id"] and tp["db_id"] in existing_tps:
                    xmind_tp_ids.add(tp["db_id"])
                    existing = existing_tps[tp["db_id"]]
                    # 与 preview 保持一致：仅当文本或描述确实变化时才计为"更新"，
                    # 否则会出现预览中 updated=0、导入后 updated=N 的不一致。
                    is_updated = (
                        tp["text"] != existing.text
                        or tp.get("description", "") != (existing.description or "")
                    )
                    if is_updated:
                        if existing.marked:
                            marked_ignored += 1
                        else:
                            await db.execute(
                                update(TestPoint)
                                .where(TestPoint.id == tp["db_id"])
                                .values(
                                    text=tp["text"],
                                    description=tp.get("description", ""),
                                    updated_at=now,
                                )
                            )
                            updated += 1
                else:
                    tp_id = tp.get("db_id") or f"tp-{uuid.uuid4().hex[:8]}"
                    xmind_tp_ids.add(tp_id)
                    new_tp = TestPoint(
                        id=tp_id,
                        split_requirement_id=matched_sr.id,
                        text=tp["text"],
                        description=tp.get("description", ""),
                        # 通过 XMind 导入新增的测试点属于人工录入，
                        # 与手动新增测试点的 source 保持一致（见 test_design.py）。
                        source="人工",
                        status="completed",
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(new_tp)
                    added += 1

        # 删除不在 XMind 中的测试点
        existing_ids = set(existing_tps.keys())
        removed_ids = existing_ids - xmind_tp_ids
        if removed_ids:
            await db.execute(
                delete(TestCase).where(TestCase.test_point_id.in_(list(removed_ids)))
            )
            await db.execute(
                delete(TestPoint).where(TestPoint.id.in_(list(removed_ids)))
            )
            deleted = len(removed_ids)

        await db.commit()

        return {
            "addedCount": added,
            "updatedCount": updated,
            "deletedCount": deleted,
            "markedIgnoredCount": marked_ignored,
        }

    def _gen_id(self) -> str:
        """生成 XMind 风格的 ID"""
        return str(uuid.uuid4()).replace('-', '')[:26]


# 单例
xmind_service = XMindService()
