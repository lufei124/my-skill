# Life Reboots 埋点基线

更新时间：2026-07-24  
来源：`游戏数据埋点.xlsx`

## 使用规则

- `游戏内上报埋点` 是现行事件表；`游戏内上报埋点（旧）` 仅作历史参考。
- 任何新增埋点前，先按事件标识符、中文名称、触发语义和分析目标检索本文件。
- 触发语义相同：复用已有事件；只缺分析维度：扩展已有事件属性；生命周期或分析语义确实不同：才新增事件。
- 已下线事件不得直接恢复使用；先确认替代事件或重新启用方案。
- 公共属性由采集框架统一补充，不要重复写入事件专属属性。
- 原始表存在命名大小写、数据来源写法和空标识符等历史不一致；维护时保留现状，新字段统一使用小写 `snake_case`。

## 标准输出格式

事件明细必须使用以下 12 列，顺序和名称不可改：

| 事件分类 | 事件名称 | 事件标识符 | 数据来源 | 埋点触发时机 | 属性名称 | 属性标识符 | 属性含义 | 上线版本 | 下线版本 | 类型 | 值含义 |
|---|---|---|---|---|---|---|---|---|---|---|---|

规则：

- 一行代表一个“事件 × 属性”；同一事件有多个属性时，逐行重复事件信息。
- 没有事件专属属性时，属性相关列留空。
- `事件标识符`、`属性标识符`使用小写 `snake_case`；沿用历史字段时保持原标识符。
- `数据来源`填写客户端、服务端或 lua；多端共同上报时明确列出。
- `上线版本`未知时写“待确认”；有效事件的`下线版本`留空。
- `类型`填写基础数据类型；`值含义`写完整枚举或格式样例。

公共属性使用独立 6 列表：

| 属性标识符 | 属性名称 | 属性含义 | 上线版本 | 下线版本 | 负责人 |
|---|---|---|---|---|---|

## 去重输出要求

每次输出埋点方案前先给出“复用判断”：`复用`、`扩展`、`新增`或`待确认`，并列出匹配到的已有事件。最终事件表仍严格使用上述 12 列，不额外插入判断列。

## 现有事件索引（93个）

格式：`事件分类｜事件名称｜事件标识符｜数据来源｜上线版本｜下线版本｜事件专属属性`

```text
基础行为｜游戏启动｜game_start｜客户端｜v1.0.1｜—｜start_type
基础行为｜启动资源更新结果｜resource_update_result｜客户端｜v1.0.1｜—｜duration_ms,is_success,error_message
基础行为｜账户创建成功｜account_create_result｜客户端｜v1.0.1｜—｜—
基础行为｜角色创建成功｜role_create_complete｜客户端｜v1.0.1｜—｜region_name,gender
基础行为｜主要页面曝光｜screen_view｜客户端｜v1.0.1｜—｜screen_name,duration,type,from
基础行为｜关键按钮点击｜button_click｜客户端｜v1.0.1｜—｜button_name
基础行为｜关键按钮点击｜new_round｜服务端｜v1.0.1｜v1.0.3｜current_age
基础行为｜行动按钮点击｜action_btn_click｜服务端｜v1.0.3｜—｜action_type,event_id
基础行为｜死亡｜role_death｜服务端｜v1.0.1｜—｜age
内容剧情｜事件触发｜event_trigger｜服务端｜v1.0.1｜—｜event_id,event_age
内容剧情｜事件完成｜event_complete｜服务端｜v1.0.1｜—｜event_id,event_age,choice_index
内容剧情｜剧情开始｜story_enter｜服务端｜v1.0.1｜—｜story_id,node_id,story_enter_age
内容剧情｜剧情中断｜story_interrupt｜服务端｜v1.0.1｜—｜duration_ms,exit_node_id
内容剧情｜剧情完成｜story_complete｜服务端｜v1.0.3｜—｜duration_ms,story_id,node_id
账号与系统｜点击绑定按钮｜bind_attempt｜客户端｜v1.0.1｜—｜entry_point,provider
账号与系统｜绑定成功｜bind_result｜客户端｜v1.0.1｜—｜provider,entry_point
账号与系统｜解除绑定成功｜unbind_result｜客户端｜v1.0.1｜—｜provider,entry_point
账号与系统｜点击切换账号｜switch_click｜客户端｜v1.0.1｜—｜entry_point
基础行为｜引导展示｜guide_show｜客户端｜v1.0.1｜—｜TargetKey
基础行为｜引导关闭｜guide_close｜客户端｜v1.0.1｜—｜TargetKey
账号与系统｜节点成功解锁｜feature_status_change｜服务端｜v1.0.1｜—｜node_id,status
账号与系统｜点击未解锁节点｜feature_locked_click｜客户端｜v1.0.1｜—｜node_id
账号与系统｜点击查看公告｜announcement_show｜客户端｜v1.0.1｜—｜notice_id,show_type
账号与系统｜收到邮件｜mail_receive｜服务端｜v1.0.1｜—｜mail_id
账号与系统｜领取邮件｜mail_reward｜服务端｜v1.0.1｜—｜—
账号与系统｜领取失败｜mail_claim_fail｜服务端｜v1.0.1｜—｜fail_reason,mail_id
账号与系统｜公告内跳转按钮点击｜notice_click_btn｜客户端｜v1.0.3｜—｜notice_id,show_type
内容剧情｜用户发送消息｜role_chat_message｜服务端｜v1.0.2｜—｜npc_id,role_age,npc_age,entrance,message_id,chat_id
内容剧情｜消息推送的点击事件｜message_push_clicked｜客户端｜v1.0.2｜—｜npc_id,is_clicked,role_id,role_age
内容剧情｜AI发送消息给用户｜npc_chat_message｜服务端｜v1.0.2｜—｜npc_id,role_age,is_proactive,npc_age,message_id,chat_id
内容剧情｜用户退出对话页面｜exit_chat｜服务端｜v1.0.2｜—｜npc_id,role_age,npc_age
内容剧情｜NPC送礼点击成功｜gift_give｜服务端｜v1.0.3｜—｜npc_id,chat_id,give_method,item_id,favor_delta
内容剧情｜好感度等级提升｜npc_favorability_level_up｜服务端｜v1.0.3｜—｜npc_id,new_level
内容剧情｜NPC视频播放｜video_play_start｜客户端｜v1.0.3｜—｜npc_id,video_url
内容剧情｜NPC视频播放结束｜video_play_end｜客户端｜v1.0.3｜—｜npc_id,video_url,play_duration
内容剧情｜NPCCG保存｜cg_save｜客户端｜v1.0.3｜—｜image_url
核心玩法｜资源变更｜resource_change｜服务端｜v1.0.2｜—｜resource_id,change_type,age,change_action,target_amount
核心玩法｜资源不足｜resource_insufficient｜服务端｜v1.0.2｜—｜change_action,age,shortage_value,current_amount
基础行为｜资源下载失败｜resource_download_failed｜客户端｜v1.0.2｜—｜resource_path,fail_reason
基础行为｜连接异常｜connection_exception｜客户端｜v1.0.2｜—｜screen_name,timestamp,exception_type
核心玩法｜跨年（新增属性）｜new_round_lua｜lua｜v1.0.2｜—｜base_attr,growth_attr,campus_attr,occu_attr,money,age,had_buff,grade,tuition,class_position,occu_id
核心玩法｜职业状态变动｜job_change｜lua｜v1.0.2｜—｜age,occu_year,occu_action,occu_before,occu_after
核心玩法｜拥有房产｜get_realty｜lua｜v1.0.2｜—｜realty_type,realty_id,get_type,realty_num
核心玩法｜出售出租房产｜out_realty｜lua｜v1.0.2｜—｜realty_out,realty_id
核心玩法｜创业后跨年｜business_round｜lua｜v1.0.2｜—｜management,store_type,store_sub,Inventory_before,Inventory_after,store_attr,rider_ship,profit_margin,manage_profit
核心玩法｜获得buff｜get_buff｜服务端｜v1.0.2｜—｜buff_id,age,base_attr
商业化-IAP｜商品曝光｜item_impression｜客户端｜v1.0.5｜—｜product_id,title,product_type,sub_type,expected_price,currency,is_first_purchase
商业化-IAP｜商品点击｜item_click｜客户端｜v1.0.5｜—｜product_id,title,product_type,sub_type,expected_price,currency,is_first_purchase
商业化-IAP｜创建订单｜order_created｜服务端｜v1.0.5｜—｜order_id,product_id,title,product_type,platform_product_id,payment_method,expected_price,currency,order_source
商业化-IAP｜调起支付｜pay_start｜客户端｜v1.0.5｜—｜order_id,product_id,product_type,platform_product_id,payment_method,expected_price,currency
商业化-IAP｜平台支付结果｜pay_result｜客户端｜v1.0.5｜—｜order_id,platform_transaction_id,product_id,product_type,payment_method,payment_result,error_code,error_message
商业化-IAA｜广告SDK初始化结果｜ad_sdk_init_result｜客户端｜v1.0.5｜—｜init_status,init_duration_ms,sdk_name,sdk_version,error_code,error_message
商业化-IAA｜广告机会触发｜ad_trigger｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_format
商业化-IAA｜激励弹窗展示｜ad_offer_show｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_format,reward_type,reward_value
商业化-IAA｜激励弹窗操作｜ad_offer_action｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,action,reward_type,reward_value
商业化-IAA｜广告策略判断结果｜ad_policy_result｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_format,decision,block_reason
商业化-IAA｜广告加载请求｜ad_load_request｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_unit_id,ad_format,load_strategy
商业化-IAA｜广告加载成功｜ad_load_success｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_unit_id,ad_format,load_strategy,network,load_duration_ms
商业化-IAA｜广告加载失败｜ad_load_fail｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_unit_id,ad_format,load_strategy,network,load_duration_ms,error_code,error_message
基础行为｜关注活动弹窗曝光｜social_event_expose｜客户端｜v1.0.3｜—｜—
基础行为｜点击去关注按钮｜social_click_follow｜客户端｜v1.0.3｜—｜platform_name
基础行为｜达成里程碑记录｜social_milestone_reach｜服务端｜v1.0.3｜—｜milestone_level
账号与系统｜提交兑换码｜redeem_code_submit｜服务端｜v1.0.3｜—｜code_string,status
账号与系统｜PV开始播放｜pv_play_start｜服务端｜v1.0.3｜—｜pv_id
账号与系统｜PV播放结束｜pv_play_end｜服务端｜v1.0.3｜—｜pv_id,end_type
基础行为｜引导触发｜guide_start｜客户端｜v1.0.3｜—｜Guideid,GuideGroupID
基础行为｜引导完成｜guide_finish｜客户端｜v1.0.3｜—｜GuideId,GuideGroupID
基础行为｜引导恢复｜guide_fallback_trigger｜客户端｜v1.0.3｜—｜GuideId,GuideGroupID
基础行为｜目标完成｜task_target_complete｜服务端｜v1.0.3｜—｜target_id
基础行为｜首包资源下载开始｜first_package_download_start｜客户端｜v1.0.3｜—｜—
基础行为｜首包资源下载完成｜first_package_download_success｜客户端｜v1.0.3｜—｜duration_ms
基础行为｜首包资源下载失败｜first_package_download_fail｜客户端｜v1.0.3｜—｜error_message,duration_ms,failed_resource_url
基础行为｜弹窗曝光｜show_resource_download_confirm_dialog｜客户端｜v1.0.3｜—｜resource_size
基础行为｜点击弹窗按钮｜resource_download_confirm_dialog_download｜客户端｜v1.0.3｜—｜click_action,resource_size
账号与系统｜注销申请提交｜account_delete_submit｜服务端｜v1.0.5｜—｜—
账号与系统｜注销成功｜account_delete_finalize｜服务端｜v1.0.5｜—｜—
基础行为｜首页侧边栏点击｜home_sidebar_click｜客户端｜v1.0.5｜—｜sidebar_id,sidebar_title,redirect_url,click_result,fail_reason
商业化-IAA｜广告库存检查｜ad_inventory_check｜客户端｜v1.0.5｜—｜ad_attempt_id,placement_id,ad_unit_id,ad_format,load_strategy,is_ready
商业化-IAA｜广告展示请求｜ad_show_request｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,ad_unit_id,ad_format
商业化-IAA｜广告开始展示｜ad_show_start｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,ad_unit_id,ad_format,network,creative_id,dsp_name,show_latency_ms
商业化-IAA｜广告展示失败｜ad_show_fail｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,ad_unit_id,ad_format,network,error_code,error_message
商业化-IAA｜广告点击｜ad_clicked｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,ad_format,network,creative_id
商业化-IAA｜获得激励资格｜ad_reward_earned｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,network,reward_type,reward_value
商业化-IAA｜广告关闭｜ad_closed｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,ad_unit_id,ad_format,network,play_duration_ms,reward_earned
商业化-IAA｜S2S奖励回调结果｜ad_s2s_reward_result｜服务端｜v1.0.5｜—｜transaction_id,show_id,ad_attempt_id,placement_id,network,verify_status,fail_reason,callback_latency_ms,reward_type,reward_value
商业化-IAA｜广告奖励发放｜ad_reward_granted｜服务端｜v1.0.5｜—｜transaction_id,show_id,ad_attempt_id,placement_id,network,grant_mode,reward_type,reward_value,grant_latency_ms
商业化-IAA｜广告奖励发放失败｜ad_reward_fail｜服务端｜v1.0.5｜—｜transaction_id,show_id,ad_attempt_id,placement_id,network,reward_type,reward_value,retry_count,fail_reason
商业化-IAA｜广告展示级收入｜ad_revenue_paid｜客户端｜v1.0.5｜—｜show_id,ad_attempt_id,placement_id,ad_unit_id,ad_format,network,revenue_value,currency
商业化-IAP｜支付成功｜pay_success｜服务端｜v1.0.5｜—｜order_id,platform_transaction_id,subscription_chain_id,product_id,title,product_type,platform_product_id,payment_method,deal_price,currency,order_source,is_first_purchase,paid_at
商业化-IAP｜支付失败｜pay_fail｜客户端/服务端｜v1.0.5｜—｜order_id,platform_transaction_id,product_id,product_type,payment_method,fail_stage,error_code,error_message
商业化-IAP｜订单关闭｜order_closed｜服务端｜v1.0.5｜—｜order_id,product_id,order_status,close_reason,payment_method
商业化-IAP｜商品发货结果｜goods_grant_result｜服务端｜v1.0.5｜—｜order_id,platform_transaction_id,product_id,product_type,grant_status,grant_content,grant_latency_ms,fail_reason,is_first_purchase
商业化-IAP｜退款成功｜refund_success｜服务端｜v1.0.5｜—｜order_id,platform_transaction_id,subscription_chain_id,product_id,product_type,payment_method,refund_price,currency,refund_reason,refunded_at
```

## 公共属性索引（26项）

`user_id`、`role_id`、`is_linked`、`pkg_type`、`uuid`、`device_id`、`platform`、`app_version`、`event_name`、`event_time`、`timezone`、`network_type`、`os_version`、`device_model`、`brand`、`country`、`register_time`、`install_time`、`language`、`session_id`、`ip`、`age`、`round`、`ab_test_group`、`is_vip`，以及一项当前缺少属性标识符的“剧情ID”。

注意：`round` 已在 v1.0.5 下线；“剧情ID”缺少标识符，应在复用前补齐或确认，不得自行猜测。
