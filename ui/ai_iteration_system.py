"""
AI迭代系统 - 整合AI学习中心、AI自主迭代、AI自动修复
AI Iteration System - Integrating AI Learning Center, AI Self-Iteration, and AI Auto-Fix
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def render_ai_iteration_system():
    """
    渲染AI迭代系统界面
    Render AI Iteration System UI
    """
    st.header("🤖 AI迭代系统")
    st.markdown("整合AI学习、自主迭代和自动修复功能的统一系统")
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 学习中心",
        "🔄 自主迭代", 
        "🛠️ 自动修复",
        "📊 系统概览"
    ])
    
    with tab1:
        render_learning_center()
    
    with tab2:
        render_self_iteration()
    
    with tab3:
        render_auto_fix()
    
    with tab4:
        render_system_overview()


def render_learning_center():
    """AI学习中心 / AI Learning Center"""
    st.markdown("### 📚 AI学习中心")
    st.info("系统会自动分析日志文件，从中学习并不断进化")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 最近学习记录")
        
        try:
            from core.ai.memory_manager import get_recent_learning
            
            learning_records = get_recent_learning()
            
            if not learning_records:
                st.warning("暂无学习记录。系统将在定时任务运行后自动生成学习记录。")
                st.info("💡 学习任务通过scheduler.py配置，默认每2小时运行一次")
            else:
                # 显示学习记录
                for idx, record in enumerate(reversed(learning_records[-20:]), 1):
                    timestamp = record.get('time', 'N/A')
                    insight = record.get('insight', '无内容')
                    confidence = record.get('confidence', 0)
                    
                    # 根据置信度显示不同颜色
                    if confidence >= 0.8:
                        st.success(f"**{idx}. {timestamp}**")
                        st.markdown(f"{insight}")
                        st.caption(f"✅ 置信度: {confidence:.0%}")
                    elif confidence >= 0.5:
                        st.info(f"**{idx}. {timestamp}**")
                        st.markdown(f"{insight}")
                        st.caption(f"ℹ️ 置信度: {confidence:.0%}")
                    else:
                        st.warning(f"**{idx}. {timestamp}**")
                        st.markdown(f"{insight}")
                        st.caption(f"⚠️ 置信度: {confidence:.0%}")
                    
                    st.markdown("---")
                
                # 统计信息
                st.markdown("#### 学习统计")
                total_records = len(learning_records)
                high_confidence = sum(1 for r in learning_records if r.get('confidence', 0) >= 0.8)
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("总学习记录", total_records)
                with col_stat2:
                    st.metric("高置信度记录", high_confidence)
        
        except Exception as e:
            st.error(f"无法加载学习记录: {e}")
            st.info("这可能是因为 memory 文件夹或文件尚未创建。当学习任务第一次运行时，它们会自动生成。")
    
    with col2:
        st.markdown("#### 学习控制")
        
        # 手动触发学习
        if st.button("🧠 立即执行学习任务", type="primary"):
            with st.spinner("AI正在学习..."):
                try:
                    from core.ai.evolution_engine import EvolutionEngine
                    
                    engine = EvolutionEngine()
                    result = engine.learn_from_logs()
                    
                    st.success("✅ 学习完成")
                    st.json(result)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"学习任务失败: {e}")
                    import traceback
                    with st.expander("查看错误详情"):
                        st.code(traceback.format_exc())
        
        st.markdown("---")
        
        # 学习配置
        st.markdown("#### 学习配置")
        
        # 显示当前配置
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                learning_interval = config.get('evolution_check_interval_hours', 2)
                st.metric("学习间隔", f"{learning_interval} 小时")
                
            except Exception as e:
                st.warning(f"无法读取配置: {e}")
        
        # 清除学习记录
        if st.button("🗑️ 清除所有学习记录"):
            if st.checkbox("确认清除？此操作不可恢复"):
                try:
                    memory_dir = "memory"
                    if os.path.exists(memory_dir):
                        for file in os.listdir(memory_dir):
                            if file.endswith('.json'):
                                os.remove(os.path.join(memory_dir, file))
                        st.success("✅ 学习记录已清除")
                        st.rerun()
                except Exception as e:
                    st.error(f"清除失败: {e}")


def render_self_iteration():
    """AI自主迭代 / AI Self-Iteration"""
    st.markdown("### 🔄 AI自主迭代")
    st.info("系统自动分析性能指标，生成优化策略并自主迭代")
    
    try:
        from core.ai.evolution_engine import EvolutionEngine
        
        engine = EvolutionEngine()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 迭代控制")
            
            if st.button("▶️ 运行一轮自主迭代", type="primary"):
                with st.spinner("AI正在自主迭代..."):
                    try:
                        result = engine.evolve()
                        
                        st.success("✅ 迭代完成")
                        
                        # 显示迭代结果
                        st.markdown("**迭代结果:**")
                        st.json(result)
                        
                        # 保存迭代记录
                        log_file = "logs/evolution_history.jsonl"
                        os.makedirs("logs", exist_ok=True)
                        
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                **result,
                                'timestamp': datetime.now().isoformat()
                            }, ensure_ascii=False) + '\n')
                        
                        st.info(f"迭代记录已保存至: {log_file}")
                        
                    except Exception as e:
                        st.error(f"迭代失败: {e}")
                        import traceback
                        with st.expander("查看错误详情"):
                            st.code(traceback.format_exc())
            
            st.markdown("---")
            
            # 自动迭代配置
            auto_iterate = st.checkbox("启用自动迭代（后台运行）", value=False)
            if auto_iterate:
                st.info("自动迭代将通过scheduler.py在后台运行")
                st.caption("默认间隔: 2小时")
        
        with col2:
            st.markdown("#### 迭代历史")
            
            # 读取迭代历史
            log_file = "logs/evolution_history.jsonl"
            
            if os.path.exists(log_file):
                try:
                    # 使用更高效的方式读取文件末尾
                    with open(log_file, 'r', encoding='utf-8') as f:
                        # 只读取最后100行以提高性能
                        lines = []
                        for line in f:
                            lines.append(line)
                            if len(lines) > 100:
                                lines.pop(0)
                    
                    st.metric("总迭代次数", len(lines))
                    
                    # 显示最近的迭代记录
                    st.markdown("**最近5次迭代:**")
                    
                    for line in reversed(lines[-5:]):
                        try:
                            record = json.loads(line)
                            timestamp = record.get('timestamp', 'N/A')
                            status = record.get('status', 'unknown')
                            
                            with st.expander(f"🔄 {timestamp[:19]} - {status}"):
                                st.json(record)
                        except (json.JSONDecodeError, Exception) as e:
                            logger.warning(f"Failed to parse iteration record: {e}")
                            continue
                            
                except Exception as e:
                    st.error(f"读取历史失败: {e}")
            else:
                st.info("暂无迭代历史")
        
        st.divider()
        
        # 迭代策略配置
        st.markdown("#### 迭代策略")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**选择器优化**")
            st.caption("自动优化网页选择器")
            optimize_selectors = st.checkbox("启用", value=True, key="opt_sel")
        
        with col2:
            st.markdown("**参数调优**")
            st.caption("优化等待时间等参数")
            optimize_params = st.checkbox("启用", value=True, key="opt_param")
        
        with col3:
            st.markdown("**错误处理**")
            st.caption("改进错误处理逻辑")
            optimize_errors = st.checkbox("启用", value=True, key="opt_err")
        
    except ImportError as e:
        st.error(f"无法加载进化引擎: {e}")
        st.info("请确保core.ai.evolution_engine模块可用")
    except Exception as e:
        st.error(f"自主迭代模块加载失败: {e}")


def render_auto_fix():
    """AI自动修复 / AI Auto-Fix"""
    st.markdown("### 🛠️ AI自动修复")
    st.info("自动检测代码问题并生成修复补丁")
    
    try:
        from core.ai.auto_patch import AutoPatcher
        
        patcher = AutoPatcher()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 错误检测与修复")
            
            # 分析日志文件
            if st.button("🔍 分析日志文件", type="primary"):
                with st.spinner("正在分析日志..."):
                    try:
                        # 读取日志文件
                        log_file = "scraper.log"
                        
                        if not os.path.exists(log_file):
                            st.warning("未找到日志文件")
                        else:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                log_content = f.read()
                            
                            # 分析错误
                            errors = analyze_log_errors(log_content)
                            
                            if errors:
                                st.error(f"检测到 {len(errors)} 个错误")
                                
                                for idx, error in enumerate(errors[:10], 1):
                                    with st.expander(f"❌ 错误 {idx}: {error.get('type', 'Unknown')}"):
                                        st.code(error.get('message', ''))
                                        st.caption(f"发生时间: {error.get('time', 'N/A')}")
                                        
                                        # 生成修复建议
                                        if st.button(f"生成修复补丁", key=f"fix_{idx}"):
                                            with st.spinner("AI正在生成修复方案..."):
                                                try:
                                                    patch = patcher.generate_patch(error)
                                                    
                                                    if patch:
                                                        st.success("✅ 修复补丁已生成")
                                                        st.code(patch, language="diff")
                                                        
                                                        if st.button(f"应用补丁", key=f"apply_fix_{idx}"):
                                                            result = patcher.apply_patch(patch)
                                                            st.success(f"补丁已应用: {result}")
                                                    else:
                                                        st.warning("无法生成修复补丁")
                                                        
                                                except Exception as e:
                                                    st.error(f"生成补丁失败: {e}")
                            else:
                                st.success("✅ 未检测到错误")
                                
                    except Exception as e:
                        st.error(f"分析失败: {e}")
                        import traceback
                        with st.expander("查看错误详情"):
                            st.code(traceback.format_exc())
        
        with col2:
            st.markdown("#### 修复历史")
            
            # 显示修复历史
            patch_dir = "patches"
            if os.path.exists(patch_dir):
                patches = [f for f in os.listdir(patch_dir) if f.endswith('.patch')]
                
                st.metric("已生成补丁", len(patches))
                
                if patches:
                    st.markdown("**最近的补丁:**")
                    for patch_file in patches[-5:]:
                        st.text(patch_file)
            else:
                st.info("暂无修复历史")
            
            st.markdown("---")
            
            # 自动修复配置
            st.markdown("#### 自动修复配置")
            auto_fix = st.checkbox("启用自动修复", value=False)
            
            if auto_fix:
                st.warning("⚠️ 自动修复会自动应用补丁，请谨慎使用")
                st.info("建议先手动审查补丁再应用")
        
    except ImportError as e:
        st.error(f"无法加载自动修复模块: {e}")
        st.info("请确保core.ai.auto_patch模块可用")
    except Exception as e:
        st.error(f"自动修复模块加载失败: {e}")


def render_system_overview():
    """系统概览 / System Overview"""
    st.markdown("### 📊 AI迭代系统概览")
    
    # 系统状态
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 学习模块")
        try:
            from core.ai.memory_manager import get_recent_learning
            records = get_recent_learning()
            st.metric("学习记录数", len(records) if records else 0)
            
            if records:
                avg_confidence = sum(r.get('confidence', 0) for r in records) / len(records)
                st.metric("平均置信度", f"{avg_confidence:.0%}")
        except:
            st.warning("学习模块未就绪")
    
    with col2:
        st.markdown("#### 迭代模块")
        try:
            log_file = "logs/evolution_history.jsonl"
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                st.metric("总迭代次数", len(lines))
                
                # 统计成功次数
                successes = sum(1 for line in lines if 'success' in line.lower())
                st.metric("成功迭代", successes)
            else:
                st.metric("总迭代次数", 0)
        except:
            st.warning("迭代模块未就绪")
    
    with col3:
        st.markdown("#### 修复模块")
        try:
            patch_dir = "patches"
            if os.path.exists(patch_dir):
                patches = [f for f in os.listdir(patch_dir) if f.endswith('.patch')]
                st.metric("生成补丁数", len(patches))
            else:
                st.metric("生成补丁数", 0)
        except:
            st.warning("修复模块未就绪")
    
    st.divider()
    
    # 工作流程图
    st.markdown("#### 🔄 AI迭代工作流程")
    
    st.markdown("""
    ```
    ┌─────────────────┐
    │  数据采集运行    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  生成日志文件    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐        ┌──────────────┐
    │  AI学习中心     │───────▶│  提取洞察    │
    │  分析日志       │        │  更新知识库   │
    └────────┬────────┘        └──────────────┘
             │
             ▼
    ┌─────────────────┐        ┌──────────────┐
    │  AI自主迭代     │───────▶│  生成策略    │
    │  优化系统       │        │  应用改进     │
    └────────┬────────┘        └──────────────┘
             │
             ▼
    ┌─────────────────┐        ┌──────────────┐
    │  AI自动修复     │───────▶│  生成补丁    │
    │  检测问题       │        │  自动修复     │
    └────────┬────────┘        └──────────────┘
             │
             ▼
    ┌─────────────────┐
    │  系统持续改进    │
    └─────────────────┘
    ```
    """)
    
    st.success("✅ AI迭代系统通过学习、迭代和修复三个模块协同工作，实现系统的持续自我进化")


def analyze_log_errors(log_content: str) -> List[Dict[str, Any]]:
    """
    分析日志文件中的错误
    Analyze errors in log file
    """
    errors = []
    
    lines = log_content.split('\n')
    
    for idx, line in enumerate(lines):
        if 'ERROR' in line or 'EXCEPTION' in line or 'CRITICAL' in line:
            # 提取错误信息
            error = {
                'line_number': idx + 1,
                'message': line,
                'type': 'ERROR' if 'ERROR' in line else 'EXCEPTION' if 'EXCEPTION' in line else 'CRITICAL'
            }
            
            # 尝试提取时间戳
            if len(line) > 19 and line[4] == '-' and line[7] == '-':
                error['time'] = line[:19]
            
            errors.append(error)
    
    return errors
