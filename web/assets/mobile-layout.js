(function() {
    'use strict';

    var isHandExpanded = false;
    var isBattleFullscreen = false;
    var userManuallyToggled = false;
    var currentBattleStage = null;
    var badgeElement = null;
    var fullscreenToggleBtn = null;
    var fullscreenMenuBtn = null;

    // =========================================================================
    // 触摸交互状态机 (Hearthstone Mobile Touch State Machine)
    // =========================================================================
    var touchState = {
        mode: 'none', // 'none' | 'card' | 'attack'
        startX: 0,
        startY: 0,
        currentX: 0,
        currentY: 0,
        isDragging: false,
        handWasCollapsed: false,
        waitingBattlecry: null,

        // 卡牌拖拽信息
        cardUid: null,
        cardId: null,
        cardElem: null,
        cardInfo: null,
        cardObj: null,
        isMinion: false,
        isSpell: false,
        isTargeted: false,
        validTargets: [],

        // 随从攻击信息
        attackerUid: null,
        attackHitbox: null,

        // 动态视觉元素
        ghostSlotEl: null,
        spellZoneEl: null,
        lastGhostPos: -1,
        hoveredTargetBtn: null
    };

    var lastDragEndTime = 0;

    function initButtons() {
        if (!fullscreenToggleBtn) {
            fullscreenToggleBtn = document.createElement('button');
            fullscreenToggleBtn.className = 'mobile-fullscreen-toggle-btn';
            fullscreenToggleBtn.setAttribute('type', 'button');
            fullscreenToggleBtn.setAttribute('title', '切换棋盘全屏模式');
            fullscreenToggleBtn.innerHTML = '<span style="font-size:13px;line-height:1">⛶</span><span>全屏</span>';

            fullscreenToggleBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                userManuallyToggled = true;
                setBattleFullscreen(!isBattleFullscreen);
            });

            document.body.appendChild(fullscreenToggleBtn);
        }

        if (!fullscreenMenuBtn) {
            fullscreenMenuBtn = document.createElement('button');
            fullscreenMenuBtn.className = 'mobile-fullscreen-menu-btn';
            fullscreenMenuBtn.setAttribute('type', 'button');
            fullscreenMenuBtn.setAttribute('title', '打开对局菜单');
            fullscreenMenuBtn.innerHTML = '<span style="font-size:13px;line-height:1">⚙️</span><span>菜单</span>';

            fullscreenMenuBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                e.preventDefault();
                var menuBtn = document.querySelector('.battle-menu-button');
                if (menuBtn) {
                    menuBtn.click();
                } else {
                    window.dispatchEvent(new KeyboardEvent('keydown', {
                        key: 'Escape',
                        code: 'Escape',
                        keyCode: 27,
                        which: 27,
                        bubbles: true
                    }));
                }
            });

            document.body.appendChild(fullscreenMenuBtn);
        }
    }

    function setBattleFullscreen(active) {
        isBattleFullscreen = !!active;
        if (isBattleFullscreen) {
            document.body.classList.add('battle-fullscreen-active');
            if (fullscreenToggleBtn) {
                fullscreenToggleBtn.innerHTML = '<span style="font-size:13px;line-height:1">🗗</span><span>取消全屏</span>';
            }
        } else {
            document.body.classList.remove('battle-fullscreen-active');
            if (fullscreenToggleBtn) {
                fullscreenToggleBtn.innerHTML = '<span style="font-size:13px;line-height:1">⛶</span><span>全屏</span>';
            }
        }
        window.dispatchEvent(new Event('resize'));
    }

    function setHandState(expanded) {
        if (!currentBattleStage) return;
        isHandExpanded = expanded;
        if (expanded) {
            currentBattleStage.classList.remove('mobile-hand-collapsed');
            currentBattleStage.classList.add('mobile-hand-expanded');
        } else {
            currentBattleStage.classList.remove('mobile-hand-expanded');
            currentBattleStage.classList.add('mobile-hand-collapsed');
        }
    }

    function attachToStage(stage) {
        currentBattleStage = stage;
        isHandExpanded = false;

        stage.classList.remove('mobile-hand-expanded');
        stage.classList.add('mobile-hand-collapsed');

        if (!stage.querySelector('.mobile-hand-minimized-badge')) {
            badgeElement = document.createElement('div');
            badgeElement.className = 'mobile-hand-minimized-badge';
            badgeElement.innerText = '👆 点击手牌展开';
            stage.appendChild(badgeElement);
        }
    }

    function checkBattleState() {
        var stage = document.querySelector('.battle-stage');
        if (stage) {
            if (!document.body.classList.contains('in-battle-view')) {
                document.body.classList.add('in-battle-view');
                if (!userManuallyToggled) {
                    setBattleFullscreen(true);
                }
            }
            if (stage !== currentBattleStage) {
                attachToStage(stage);
            }

            var endTurnBtn = stage.querySelector('.end-turn-button');
            if (endTurnBtn && !endTurnBtn.classList.contains('your-turn')) {
                if (isHandExpanded) {
                    setHandState(false);
                }
            }
        } else {
            if (document.body.classList.contains('in-battle-view')) {
                document.body.classList.remove('in-battle-view');
            }
            if (isBattleFullscreen) {
                setBattleFullscreen(false);
            }
            currentBattleStage = null;
            isHandExpanded = false;
            userManuallyToggled = false;
        }
    }

    // =========================================================================
    // 坐标与箭头管理 (Pixi Coordinate Conversion & Arrow Helpers)
    // =========================================================================
    function getStageCoords(clientX, clientY) {
        var boardEl = document.querySelector('.board-surface');
        if (!boardEl) return { x: 800, y: 526 };
        var rect = boardEl.getBoundingClientRect();
        if (!rect.width || !rect.height) return { x: 800, y: 526 };
        return {
            x: (clientX - rect.left) / rect.width * 1600,
            y: (clientY - rect.top) / rect.height * 900
        };
    }

    function updateArrow(originId, fromEl, clientX, clientY) {
        if (!window.__hsPixi || typeof window.__hsPixi.setArrow !== 'function') return;
        var targetCoords = getStageCoords(clientX, clientY);
        var startCoords = void 0;
        if (fromEl) {
            var boardEl = document.querySelector('.board-surface');
            if (boardEl) {
                var bRect = boardEl.getBoundingClientRect();
                var fRect = fromEl.getBoundingClientRect();
                startCoords = {
                    x: (fRect.left + fRect.width / 2 - bRect.left) / bRect.width * 1600,
                    y: (fRect.top + fRect.height / 2 - bRect.top) / bRect.height * 900
                };
            }
        }
        window.__hsPixi.setArrow(originId, targetCoords, startCoords);
    }

    function clearArrow() {
        if (window.__hsPixi && typeof window.__hsPixi.setArrow === 'function') {
            window.__hsPixi.setArrow(null, null);
        }
    }

    // =========================================================================
    // 战场与手牌区域检测 (Area Detection Helpers)
    // =========================================================================
    function isOverFriendlyBoard(clientX, clientY) {
        var boardEl = document.querySelector('.board-surface');
        if (!boardEl) return false;
        var rect = boardEl.getBoundingClientRect();
        // 我方随从排布区域在棋盘高度的大约 38% ~ 82% 之间
        var minY = rect.top + rect.height * 0.38;
        var maxY = rect.top + rect.height * 0.82;
        var minX = rect.left + rect.width * 0.04;
        var maxX = rect.right - rect.width * 0.04;
        return clientY >= minY && clientY <= maxY && clientX >= minX && clientX <= maxX;
    }

    function isOutOfHand(clientX, clientY) {
        var boardEl = document.querySelector('.board-surface');
        if (boardEl) {
            var rect = boardEl.getBoundingClientRect();
            // 只要手指拉出底部手牌区（进入棋盘上部约 82% 的广阔战场区域）
            return clientY < rect.bottom - rect.height * 0.18;
        }
        return clientY < window.innerHeight * 0.72;
    }

    // =========================================================================
    // 高精度目标拾取 (DOM + 物理坐标复合拾取器，保证手机端点击100%命中目标)
    // =========================================================================
    function findTargetAtCoords(clientX, clientY, validTargets) {
        var targetsSet = null;
        if (validTargets && Array.isArray(validTargets)) {
            targetsSet = new Set(validTargets);
        }

        // 1. DOM 拾取：遍历触控点下所有的元素
        if (typeof document.elementsFromPoint === 'function') {
            var elements = document.elementsFromPoint(clientX, clientY);
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                var tid = el.getAttribute ? el.getAttribute('data-target') : null;
                if (!tid && el.closest) {
                    var hb = el.closest('.board-hitbox');
                    if (hb) tid = hb.getAttribute('data-target');
                }
                if (tid && (!targetsSet || targetsSet.has(tid))) {
                    return tid;
                }
            }
        }

        // 2. 物理坐标临近判定（绝对保底，防止由于按键透明、Canvas穿透或点击边缘导致未命中）
        var stage = getStageCoords(clientX, clientY);
        var bestId = null;
        var bestDist = 180; // 宽容度 180 像素（手机大拇指点击极其灵敏）

        // 若全局提供了准确的 actor 坐标映射（VG 算法返回）：
        if (window.__hsBattle && typeof window.__hsBattle.getActorPositions === 'function') {
            try {
                var actorMap = window.__hsBattle.getActorPositions();
                if (actorMap && actorMap.forEach) {
                    actorMap.forEach(function(pos, uid) {
                        if (!targetsSet || targetsSet.has(uid)) {
                            var d = Math.hypot(stage.x - pos.x, stage.y - pos.y);
                            if (d < bestDist) {
                                bestDist = d;
                                bestId = uid;
                            }
                        }
                    });
                    if (bestId) return bestId;
                }
            } catch (err) {}
        }

        // 敌方英雄 hero-1 (Pixi坐标: x=800, y=151)
        if (!targetsSet || targetsSet.has('hero-1')) {
            var dH1 = Math.hypot(stage.x - 800, stage.y - 151);
            if (dH1 < bestDist) {
                bestDist = dH1;
                bestId = 'hero-1';
            }
        }

        // 我方英雄 hero-0 (Pixi坐标: x=800, y=696)
        if (!targetsSet || targetsSet.has('hero-0')) {
            var dH0 = Math.hypot(stage.x - 800, stage.y - 696);
            if (dH0 < bestDist) {
                bestDist = dH0;
                bestId = 'hero-0';
            }
        }

        // 场上随从 (从全局游戏状态读取坐标，精准对齐棋盘上每个随从)
        if (window.__hsBattle && window.__hsBattle.state && window.__hsBattle.state.players) {
            var p0Board = window.__hsBattle.state.players[0].board;
            var p1Board = window.__hsBattle.state.players[1].board;

            // 敌方随从 (y = 355)
            var N1 = p1Board.length;
            p1Board.forEach(function(m, idx) {
                if (!targetsSet || targetsSet.has(m.uid)) {
                    var mX = 800 - (N1 - 1) * 60 + idx * 120;
                    var mY = 355;
                    var dM = Math.hypot(stage.x - mX, stage.y - mY);
                    if (dM < bestDist) {
                        bestDist = dM;
                        bestId = m.uid;
                    }
                }
            });

            // 我方随从 (y = 526)
            var N0 = p0Board.length;
            p0Board.forEach(function(m, idx) {
                if (!targetsSet || targetsSet.has(m.uid)) {
                    var mX = 800 - (N0 - 1) * 60 + idx * 120;
                    var mY = 526;
                    var dM = Math.hypot(stage.x - mX, stage.y - mY);
                    if (dM < bestDist) {
                        bestDist = dM;
                        bestId = m.uid;
                    }
                }
            });
        }

        return bestId;
    }

    // =========================================================================
    // 随从动态挤开缝隙与上场预览 (完全复刻战场图标：框体、嘲讽框、数值 + 暗蓝色遮罩)
    // =========================================================================
    function setMinionParting(pos) {
        if (!window.__hsBattle || !window.__hsBattle.state || !window.__hsPixi || !window.__hsPixi.actors) return;
        var myMinions = window.__hsBattle.state.players[0].board;
        var N = myMinions.length;
        myMinions.forEach(function(m, idx) {
            var targetIdx = pos === -1 ? idx : (idx < pos ? idx : idx + 1);
            var targetX = pos === -1 ? (800 - (N - 1) * 60 + idx * 120) : (800 - N * 60 + targetIdx * 120);
            var actor = window.__hsPixi.actors.get(m.uid);
            if (actor) {
                actor.position.x = targetX;
            }
            var hitbox = document.querySelector('[data-target="' + m.uid + '"]');
            if (hitbox) {
                hitbox.style.left = (targetX / 1600 * 100) + '%';
            }
        });
        window.__hsPixi.dirty = true;
    }

    function ensureGhostSlot(cardId, cardInfo) {
        if (!touchState.ghostSlotEl) {
            var ghost = document.createElement('div');
            var isTaunt = cardInfo ? (
                (cardInfo.mechanics && cardInfo.mechanics.indexOf('TAUNT') !== -1) ||
                (cardInfo.rule && cardInfo.rule.taunt)
            ) : false;

            ghost.className = 'minion-placement-ghost' + (isTaunt ? ' has-taunt' : '');

            var html = '';
            // 1. 嘲讽石盾外框 (复刻战场原版石质盾牌造型)
            if (isTaunt) {
                html += '<svg class="ghost-taunt-svg" viewBox="-62 -82 124 168" preserveAspectRatio="none">' +
                        '<path d="M -44 -74 L 44 -74 L 56 -45 L 55 40 L 0 80 L -55 40 L -56 -45 Z" fill="#555860" stroke="#bcc5d3" stroke-width="5.5" stroke-linejoin="round" />' +
                        '<path d="M -44 -74 L 44 -74 L 56 -45 L 55 40 L 0 80 L -55 40 L -56 -45 Z" fill="rgba(12, 35, 85, 0.65)" />' +
                        '</svg>';
            }

            // 2. 随从标准椭圆身躯与原画
            var artUrl = '';
            if (window.__hsBattle && typeof window.__hsBattle.cardArt === 'function') {
                artUrl = window.__hsBattle.cardArt(cardId);
            }
            if (!artUrl && touchState.cardElem) {
                var cardImg = touchState.cardElem.querySelector('img');
                if (cardImg) artUrl = cardImg.src;
            }

            html += '<div class="ghost-oval-body">' +
                    '<img class="minion-ghost-art" src="' + (artUrl || '') + '" alt="" />' +
                    '<div class="minion-ghost-mask"></div>' +
                    '</div>';

            // 3. 随从身材角标数值 (左下黄色圆形攻击，右下红色圆形生命)
            if (cardInfo) {
                if (cardInfo.attack !== undefined) {
                    html += '<div class="ghost-stat ghost-atk">' + cardInfo.attack + '</div>';
                }
                if (cardInfo.health !== undefined) {
                    html += '<div class="ghost-stat ghost-hp">' + cardInfo.health + '</div>';
                }
            }

            ghost.innerHTML = html;

            var boardEl = document.querySelector('.board-surface');
            if (boardEl) {
                boardEl.appendChild(ghost);
            }
            touchState.ghostSlotEl = ghost;
        }
        return touchState.ghostSlotEl;
    }

    function removeGhostSlot() {
        if (touchState.ghostSlotEl) {
            if (touchState.ghostSlotEl.parentNode) {
                touchState.ghostSlotEl.parentNode.removeChild(touchState.ghostSlotEl);
            }
            touchState.ghostSlotEl = null;
        }
        touchState.lastGhostPos = -1;
    }

    function ensureSpellCastingZone() {
        if (!touchState.spellZoneEl) {
            var zone = document.createElement('div');
            zone.className = 'spell-casting-zone';
            zone.innerHTML = '<span>⚡ 松手在此施放法术</span>';
            var boardEl = document.querySelector('.board-surface');
            if (boardEl) {
                boardEl.appendChild(zone);
            }
            touchState.spellZoneEl = zone;
        }
        return touchState.spellZoneEl;
    }

    function removeSpellCastingZone() {
        if (touchState.spellZoneEl) {
            if (touchState.spellZoneEl.parentNode) {
                touchState.spellZoneEl.parentNode.removeChild(touchState.spellZoneEl);
            }
            touchState.spellZoneEl = null;
        }
    }

    function highlightHoveredTarget(targetBtn) {
        if (touchState.hoveredTargetBtn === targetBtn) return;
        if (touchState.hoveredTargetBtn) {
            touchState.hoveredTargetBtn.classList.remove('target-hovered');
        }
        touchState.hoveredTargetBtn = targetBtn;
        if (touchState.hoveredTargetBtn) {
            touchState.hoveredTargetBtn.classList.add('target-hovered');
        }
    }

    // =========================================================================
    // 触摸事件监听系统 (Native Mobile Touch Handlers)
    // =========================================================================
    function onTouchStart(e) {
        if (!currentBattleStage || e.touches.length > 1) return;
        var touch = e.touches[0];
        var target = touch.target;

        // 避开基础全局按钮
        if (target.closest && (
            target.closest('.mobile-fullscreen-toggle-btn') || 
            target.closest('.mobile-fullscreen-menu-btn') ||
            target.closest('.battle-menu-button') ||
            target.closest('.end-turn-button') ||
            target.closest('.tracker-toggle')
        )) {
            return;
        }

        // 每次触碰开始时，严格重置 isDragging 为 false
        touchState.isDragging = false;
        touchState.startX = touch.clientX;
        touchState.startY = touch.clientY;
        touchState.currentX = touch.clientX;
        touchState.currentY = touch.clientY;

        // 确保未完成的随从分缝状态全部安全复位
        if (touchState.lastGhostPos !== -1) {
            touchState.lastGhostPos = -1;
            setMinionParting(-1);
            removeGhostSlot();
        }

        // 0. 随从战吼等待选目标阶段：记录起点，在 touchend 时高精度触发点选！
        var isWaitingBattlecry = !!(
            touchState.waitingBattlecry ||
            (window.__hsBattle && window.__hsBattle.pendingBattlecry) ||
            (window.__hsBattle && window.__hsBattle.selection && 
             window.__hsBattle.selection.kind === 'card' && window.__hsBattle.selection.position !== undefined)
        );
        var isWaitingPowerTarget = !!(
            window.__hsBattle && window.__hsBattle.selection && window.__hsBattle.selection.kind === 'power'
        );
        if (isWaitingBattlecry || isWaitingPowerTarget) {
            return;
        }

        // 1. 触摸手牌：无论手牌是否折叠，都记录状态，支持无延时直接拖拽出牌！
        var handCard = target.closest ? target.closest('.hand-card') : null;
        if (handCard) {
            var isPlayerTurn = window.__hsBattle && (window.__hsBattle.isPlayerTurn ? window.__hsBattle.isPlayerTurn() : window.__hsBattle.state?.activePlayer === 0);
            if (!isPlayerTurn) return;
            var cardUid = handCard.getAttribute('data-hand-uid');
            var cardId = handCard.getAttribute('data-card-id');
            var isPlayable = window.__hsBattle.isCardPlayable ? 
                window.__hsBattle.isCardPlayable(cardUid) : 
                (window.__hsBattle.playableUids && window.__hsBattle.playableUids.has(cardUid));
            if (!isPlayable) return;

            var cardInfo = window.__hsBattle.cardDict ? window.__hsBattle.cardDict(cardId) : null;
            var isMinion = cardInfo ? (cardInfo.type === 'MINION' || cardInfo.type === 'WEAPON') : false;
            var isSpell = cardInfo ? (cardInfo.type === 'SPELL') : false;
            var cardObj = window.__hsBattle.hand ? window.__hsBattle.hand.find(function(c) { return c.uid === cardUid; }) : null;
            var targets = (cardObj && window.__hsBattle.getCardTargets) ? window.__hsBattle.getCardTargets(cardObj, 0) : [];
            var isTargeted = isSpell && targets && targets.length > 0;

            touchState.mode = 'card';
            touchState.isDragging = false;
            touchState.handWasCollapsed = !isHandExpanded;
            touchState.cardUid = cardUid;
            touchState.cardId = cardId;
            touchState.cardElem = handCard;
            touchState.cardInfo = cardInfo;
            touchState.cardObj = cardObj;
            touchState.isMinion = isMinion;
            touchState.isSpell = isSpell;
            touchState.isTargeted = isTargeted;
            touchState.validTargets = targets || [];
            touchState.lastGhostPos = -1;
            return;
        }

        // 1.5 触摸英雄技能：支持长按/滑动拖拽施放目标英雄技能（如法师火球、牧师治疗），非指向性技能支持拖入战场或点击施放
        var powerHitbox = target.closest ? target.closest('.power-hitbox') : null;
        if (!powerHitbox && target.closest) {
            var hb = target.closest('.board-hitbox');
            if (hb && (hb.getAttribute('data-testid') === 'hero-power' || hb.classList.contains('power-hitbox'))) {
                powerHitbox = hb;
            }
        }
        if (!powerHitbox) {
            var stage = getStageCoords(touch.clientX, touch.clientY);
            if (Math.hypot(stage.x - 989, stage.y - 711) < 65) {
                powerHitbox = document.querySelector('.power-hitbox');
            }
        }
        if (powerHitbox && window.__hsBattle) {
            var canUse = window.__hsBattle.canUseHeroPower ? window.__hsBattle.canUseHeroPower() : !powerHitbox.disabled;
            if (canUse) {
                var isTargeted = window.__hsBattle.isHeroPowerTargeted ? window.__hsBattle.isHeroPowerTargeted() : false;
                var powerTargets = window.__hsBattle.getHeroPowerTargets ? window.__hsBattle.getHeroPowerTargets() : [];

                if (isTargeted && powerTargets && powerTargets.length > 0) {
                    touchState.mode = 'power';
                    touchState.isDragging = false;
                    touchState.powerHitbox = powerHitbox;
                    touchState.validTargets = powerTargets;
                    return;
                } else if (!isTargeted) {
                    touchState.mode = 'power_untargeted';
                    touchState.isDragging = false;
                    touchState.powerHitbox = powerHitbox;
                    touchState.validTargets = [];
                    return;
                }
            }
        }

        // 2. 触摸场上就绪随从或英雄：准备拖动攻击
        var atkHitbox = target.closest ? target.closest('.board-hitbox') : null;
        if (!atkHitbox) {
            var nearbyTarget = findTargetAtCoords(touch.clientX, touch.clientY);
            if (nearbyTarget) {
                var el = document.querySelector('.board-hitbox[data-target="' + nearbyTarget + '"]');
                if (el) atkHitbox = el;
            }
        }
        if (atkHitbox && window.__hsBattle) {
            var targetId = atkHitbox.getAttribute('data-target');
            if (targetId && window.__hsBattle.canAttack && window.__hsBattle.canAttack(targetId)) {
                var attackTargets = window.__hsBattle.getAttackTargets ? window.__hsBattle.getAttackTargets(targetId) : [];
                if (attackTargets && attackTargets.length > 0) {
                    touchState.mode = 'attack';
                    touchState.isDragging = false;
                    touchState.attackerUid = targetId;
                    touchState.attackHitbox = atkHitbox;
                    touchState.validTargets = attackTargets;
                    return;
                }
            }
        }
    }

    function onTouchMove(e) {
        var isWaitingBattlecry = !!(
            touchState.waitingBattlecry ||
            (window.__hsBattle && window.__hsBattle.pendingBattlecry) ||
            (window.__hsBattle && window.__hsBattle.selection && 
             window.__hsBattle.selection.kind === 'card' && window.__hsBattle.selection.position !== undefined)
        );
        var isWaitingPowerTarget = !!(
            window.__hsBattle && window.__hsBattle.selection && window.__hsBattle.selection.kind === 'power'
        );
        if (isWaitingBattlecry || isWaitingPowerTarget) return;

        if (touchState.mode === 'none') return;
        var touch = e.touches[0];
        touchState.currentX = touch.clientX;
        touchState.currentY = touch.clientY;
        var dist = Math.hypot(touchState.currentX - touchState.startX, touchState.currentY - touchState.startY);

        // 手指滑动超过 8 像素或向上拖拽超过 6 像素：立即进入直接拖拽模式（无需等待长按）
        if (!touchState.isDragging) {
            if (dist > 8 || (touchState.startY - touchState.currentY > 6)) {
                touchState.isDragging = true;
                e.preventDefault();

                // 若手牌此前处于折叠状态，拖拽开始时自动展开
                if (!isHandExpanded) {
                    setHandState(true);
                }

                if (touchState.cardElem) {
                    touchState.cardElem.classList.add('mobile-drag-source');
                }

                if (touchState.mode === 'card') {
                    if (touchState.isTargeted) {
                        // 指向性法术：直接拉出指向目标箭头
                        updateArrow(touchState.cardUid, touchState.cardElem, touchState.currentX, touchState.currentY);
                    }
                } else if (touchState.mode === 'attack') {
                    if (window.__hsBattle && window.__hsBattle.onAttackStart) {
                        window.__hsBattle.onAttackStart(touchState.attackerUid);
                    }
                    updateArrow(touchState.attackerUid, touchState.attackHitbox, touchState.currentX, touchState.currentY);
                } else if (touchState.mode === 'power') {
                    updateArrow('power-0', touchState.powerHitbox, touchState.currentX, touchState.currentY);
                }
            }
            return;
        }

        // 已在拖拽中：阻止默认行为
        e.preventDefault();

        // 1. 随从卡牌拖拽：动态计算战场插槽并预览缝隙与暗蓝色椭圆小图（无白框卡牌）
        if (touchState.mode === 'card' && touchState.isMinion) {
            var overFriendly = isOverFriendlyBoard(touchState.currentX, touchState.currentY);
            if (overFriendly && window.__hsBattle && window.__hsBattle.calcMinionPos) {
                var pos = window.__hsBattle.calcMinionPos(touchState.currentX);
                if (pos !== touchState.lastGhostPos) {
                    touchState.lastGhostPos = pos;
                    // 场上已有生物平滑挤开缝隙
                    setMinionParting(pos);

                    // 椭圆小图插槽（完全复刻随从框体、嘲讽框、身材数值 + 暗蓝色遮罩）定位在缝隙处
                    var ghost = ensureGhostSlot(touchState.cardId, touchState.cardInfo);
                    var myMinions = window.__hsBattle.state.players[0].board;
                    var N = myMinions.length;
                    var slotX = ((800 - N * 60 + pos * 120) / 1600) * 100;
                    ghost.style.left = slotX + '%';
                    ghost.style.top = '58.4%';
                    ghost.style.display = 'block';
                }
            } else {
                if (touchState.lastGhostPos !== -1) {
                    touchState.lastGhostPos = -1;
                    setMinionParting(-1);
                    if (touchState.ghostSlotEl) {
                        touchState.ghostSlotEl.style.display = 'none';
                    }
                }
            }
            return;
        }

        // 2. 指向性法术：箭头实时跟随手指并高亮合法目标
        if (touchState.mode === 'card' && touchState.isTargeted) {
            updateArrow(touchState.cardUid, touchState.cardElem, touchState.currentX, touchState.currentY);
            var tid = findTargetAtCoords(touchState.currentX, touchState.currentY, touchState.validTargets);
            var targetBtn = tid ? document.querySelector('[data-target="' + tid + '"]') : null;
            highlightHoveredTarget(targetBtn);
            return;
        }

        // 3. 全局/无目标法术：拖出至战场显示施法光环（无白边框卡牌），拖回手牌取消
        if (touchState.mode === 'card' && touchState.isSpell && !touchState.isTargeted) {
            if (isOutOfHand(touchState.currentX, touchState.currentY)) {
                var zone = ensureSpellCastingZone();
                zone.style.display = 'flex';
            } else {
                if (touchState.spellZoneEl) {
                    touchState.spellZoneEl.style.display = 'none';
                }
            }
            return;
        }

        // 4. 随从/英雄攻击：箭头实时跟随手指并高亮敌方目标
        if (touchState.mode === 'attack') {
            updateArrow(touchState.attackerUid, touchState.attackHitbox, touchState.currentX, touchState.currentY);
            var atkTid = findTargetAtCoords(touchState.currentX, touchState.currentY, touchState.validTargets);
            var atkBtn = atkTid ? document.querySelector('[data-target="' + atkTid + '"]') : null;
            highlightHoveredTarget(atkBtn);
            return;
        }

        // 5. 指向性英雄技能：箭头实时跟随手指并高亮合法目标
        if (touchState.mode === 'power') {
            updateArrow('power-0', touchState.powerHitbox, touchState.currentX, touchState.currentY);
            var pTid = findTargetAtCoords(touchState.currentX, touchState.currentY, touchState.validTargets);
            var pBtn = pTid ? document.querySelector('[data-target="' + pTid + '"]') : null;
            highlightHoveredTarget(pBtn);
            return;
        }

        // 6. 非指向性英雄技能：拖向战场中心显示施法光环
        if (touchState.mode === 'power_untargeted') {
            if (isOutOfHand(touchState.currentX, touchState.currentY)) {
                var zone = ensureSpellCastingZone();
                zone.style.display = 'flex';
            } else {
                if (touchState.spellZoneEl) {
                    touchState.spellZoneEl.style.display = 'none';
                }
            }
            return;
        }
    }

    function onTouchEnd(e) {
        // 0. 随从战吼等待选目标阶段的点选处理 (核心修复：解决提示“请选择卡牌的目标”但点选无响应问题)
        var isWaitingBattlecry = !!(
            touchState.waitingBattlecry ||
            (window.__hsBattle && window.__hsBattle.pendingBattlecry) ||
            (window.__hsBattle && window.__hsBattle.selection && 
             window.__hsBattle.selection.kind === 'card' && window.__hsBattle.selection.position !== undefined)
        );

        // 0.5 英雄技能等待选目标阶段的点选处理
        var isWaitingPowerTarget = !!(
            window.__hsBattle && window.__hsBattle.selection && window.__hsBattle.selection.kind === 'power'
        );
        if (isWaitingPowerTarget) {
            var touch = e.changedTouches ? e.changedTouches[0] : (e.touches ? e.touches[0] : null);
            var endX = touch ? touch.clientX : touchState.currentX;
            var endY = touch ? touch.clientY : touchState.currentY;
            var tapDist = Math.hypot(endX - touchState.startX, endY - touchState.startY);
            if (tapDist < 60) {
                e.preventDefault();
                lastDragEndTime = Date.now();
                var validTargets = window.__hsBattle.targets || (window.__hsBattle.getHeroPowerTargets ? window.__hsBattle.getHeroPowerTargets() : []);
                var targetId = findTargetAtCoords(endX, endY, validTargets);
                if (targetId) {
                    if (window.__hsBattle && window.__hsBattle.useHeroPower) {
                        window.__hsBattle.useHeroPower(targetId);
                    } else if (window.__hsBattle && window.__hsBattle.onTarget) {
                        window.__hsBattle.onTarget(targetId);
                    }
                } else {
                    if (window.__hsBattle && window.__hsBattle.cancel) {
                        window.__hsBattle.cancel();
                    }
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.isDragging = false;
            touchState.mode = 'none';
            return;
        }

        if (isWaitingBattlecry) {
            var touch = e.changedTouches ? e.changedTouches[0] : (e.touches ? e.touches[0] : null);
            var endX = touch ? touch.clientX : touchState.currentX;
            var endY = touch ? touch.clientY : touchState.currentY;
            var tapDist = Math.hypot(endX - touchState.startX, endY - touchState.startY);

            // 宽容度 60 像素：全面屏手机轻微滑动或自然手指接触仍视作点选
            if (tapDist < 60) {
                e.preventDefault();
                lastDragEndTime = Date.now();

                var pending = (window.__hsBattle && window.__hsBattle.pendingBattlecry) || touchState.waitingBattlecry;
                var validTargets = (pending && pending.targets) ? pending.targets : (window.__hsBattle ? window.__hsBattle.targets : []);
                var targetId = findTargetAtCoords(endX, endY, validTargets);

                if (targetId) {
                    // 点击到了有效目标：优先通过 selectBattlecryTarget 彻底直调出牌！
                    if (window.__hsBattle && window.__hsBattle.selectBattlecryTarget) {
                        window.__hsBattle.selectBattlecryTarget(targetId);
                    } else if (window.__hsBattle && window.__hsBattle.onTarget) {
                        window.__hsBattle.onTarget(targetId);
                    } else if (window.__hsBattle && window.__hsBattle.dispatch) {
                        var sel = pending || window.__hsBattle.selection;
                        window.__hsBattle.dispatch({
                            type: "PLAY_CARD",
                            player: 0,
                            uid: sel.uid,
                            position: sel.position,
                            target: targetId,
                            choice: sel.choice
                        });
                        if (window.__hsBattle.cancel) window.__hsBattle.cancel();
                    }
                } else {
                    // 点击了空白区域或无效目标：撤回放置（随从收回手牌）！
                    if (window.__hsBattle && window.__hsBattle.cancelBattlecry) {
                        window.__hsBattle.cancelBattlecry();
                    } else if (window.__hsBattle && window.__hsBattle.cancel) {
                        window.__hsBattle.cancel();
                    }
                }
            } else {
                // 拖动距离过大：视为放弃出牌并取消
                if (window.__hsBattle && window.__hsBattle.cancelBattlecry) {
                    window.__hsBattle.cancelBattlecry();
                } else if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }

            touchState.waitingBattlecry = null;
            touchState.isDragging = false;
            touchState.mode = 'none';
            return;
        }

        if (touchState.mode === 'none') {
            touchState.isDragging = false;
            return;
        }

        // 若未拖动（属于轻触/点击）：
        if (!touchState.isDragging) {
            if (touchState.mode === 'card') {
                if (touchState.handWasCollapsed) {
                    // 若此前是折叠状态，单击卡牌展开手牌
                    setHandState(true);
                } else {
                    // 若此前已展开，仅处理抉择卡牌弹窗；彻底取消双击/单击直接施放非指向性法术，杜绝误触！
                    if (touchState.cardInfo && (touchState.cardInfo.rule?.chooseOne || touchState.cardInfo.mechanics?.includes('CHOOSE_ONE'))) {
                        if (window.__hsBattle && window.__hsBattle.onPlayClick) {
                            window.__hsBattle.onPlayClick(touchState.cardObj);
                        }
                    }
                }
            } else if (touchState.mode === 'power') {
                // 点击指向性英雄技能：进入选目标态
                if (window.__hsBattle && window.__hsBattle.setSelection) {
                    window.__hsBattle.setSelection({ kind: 'power' });
                }
            } else if (touchState.mode === 'power_untargeted') {
                // 点击非指向性英雄技能：直接施放
                if (window.__hsBattle && window.__hsBattle.useHeroPower) {
                    window.__hsBattle.useHeroPower();
                }
            }
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        e.preventDefault();
        lastDragEndTime = Date.now();

        // 关键修复：必须在清除视觉元素前抓取有效判定位置！
        var currentMode = touchState.mode;
        var currentCardUid = touchState.cardUid;
        var isMinion = touchState.isMinion;
        var isSpell = touchState.isSpell;
        var isTargeted = touchState.isTargeted;
        var validTargets = touchState.validTargets;
        var finalMinionPos = touchState.lastGhostPos;
        var clientX = touchState.currentX;
        var clientY = touchState.currentY;

        // 1. 清理所有动态视觉元素
        highlightHoveredTarget(null);
        clearArrow();
        removeGhostSlot();
        removeSpellCastingZone();
        setMinionParting(-1);
        if (touchState.cardElem) {
            touchState.cardElem.classList.remove('mobile-drag-source');
        }

        // 2. 随从松手逻辑：若在战场随从区（finalMinionPos !== -1），则上场！
        if (currentMode === 'card' && isMinion) {
            if (finalMinionPos !== -1) {
                if (window.__hsBattle && window.__hsBattle.playCardDirect) {
                    var res = window.__hsBattle.playCardDirect(currentCardUid, finalMinionPos);
                    if (res && res.needTarget) {
                        // 进入指向性战吼选目标阶段：保持等待，重置拖拽标记，由下一步用户点击目标决定！
                        touchState.waitingBattlecry = res;
                        touchState.isDragging = false;
                        touchState.mode = 'none';
                        return;
                    }
                } else if (window.__hsBattle && window.__hsBattle.onPosition) {
                    window.__hsBattle.onPosition(finalMinionPos);
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.waitingBattlecry = null;
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        // 3. 指向性法术松手逻辑：指向有效目标施放，无效或拖回手牌撤回
        if (currentMode === 'card' && isTargeted) {
            var targetId = findTargetAtCoords(clientX, clientY, validTargets);
            if (targetId) {
                if (window.__hsBattle && window.__hsBattle.playCardDirect) {
                    window.__hsBattle.playCardDirect(currentCardUid, void 0, targetId);
                } else if (window.__hsBattle && window.__hsBattle.onTarget) {
                    window.__hsBattle.onTarget(targetId);
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        // 4. 全局/无目标法术松手逻辑：拖出手牌至战场即施放，拖回手牌撤回
        if (currentMode === 'card' && isSpell && !isTargeted) {
            if (isOutOfHand(clientX, clientY)) {
                if (window.__hsBattle && window.__hsBattle.playCardDirect) {
                    window.__hsBattle.playCardDirect(currentCardUid);
                } else if (window.__hsBattle && window.__hsBattle.dispatch) {
                    window.__hsBattle.dispatch({ type: "PLAY_CARD", player: 0, uid: currentCardUid });
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        // 5. 随从/英雄攻击松手逻辑：拖向目标发动攻击，支持队列化直接攻击！
        if (currentMode === 'attack') {
            var atkTid = findTargetAtCoords(clientX, clientY, validTargets);
            if (atkTid) {
                if (window.__hsBattle && window.__hsBattle.queueAttack) {
                    window.__hsBattle.queueAttack(touchState.attackerUid, atkTid);
                } else if (window.__hsBattle && window.__hsBattle.onTarget) {
                    window.__hsBattle.onTarget(atkTid);
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        // 6. 指向性英雄技能松手逻辑：拖向合法目标发动技能，拖至空白或手牌撤回
        if (currentMode === 'power') {
            var pTid = findTargetAtCoords(clientX, clientY, validTargets);
            if (pTid) {
                if (window.__hsBattle && window.__hsBattle.useHeroPower) {
                    window.__hsBattle.useHeroPower(pTid);
                } else if (window.__hsBattle && window.__hsBattle.dispatch) {
                    window.__hsBattle.dispatch({ type: "HERO_POWER", player: 0, target: pTid });
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        // 7. 非指向性英雄技能松手逻辑：拖入战场即释放，拖回技能处撤回
        if (currentMode === 'power_untargeted') {
            if (isOutOfHand(clientX, clientY)) {
                if (window.__hsBattle && window.__hsBattle.useHeroPower) {
                    window.__hsBattle.useHeroPower();
                } else if (window.__hsBattle && window.__hsBattle.dispatch) {
                    window.__hsBattle.dispatch({ type: "HERO_POWER", player: 0 });
                }
            } else {
                if (window.__hsBattle && window.__hsBattle.cancel) {
                    window.__hsBattle.cancel();
                }
            }
            touchState.mode = 'none';
            touchState.isDragging = false;
            return;
        }

        touchState.mode = 'none';
        touchState.isDragging = false;
    }

    // 点击空白处收起手牌与处理折叠展开
    function handleInteraction(e) {
        if (!currentBattleStage) return;
        // 防抖：拖拽刚结束时的合成点击不触发背景交互
        if (Date.now() - lastDragEndTime < 350) return;

        // 如果正处于战吼选目标阶段，交给 touchend 的专业判定，不在此处误判取消
        var isWaitingBattlecry = !!(
            touchState.waitingBattlecry ||
            (window.__hsBattle && window.__hsBattle.pendingBattlecry) ||
            (window.__hsBattle && window.__hsBattle.selection && 
             window.__hsBattle.selection.kind === 'card' && window.__hsBattle.selection.position !== undefined)
        );
        var isWaitingPowerTarget = !!(
            window.__hsBattle && window.__hsBattle.selection && window.__hsBattle.selection.kind === 'power'
        );
        if (isWaitingBattlecry || isWaitingPowerTarget) return;

        var target = e.target;
        if (target && target.closest && (
            target.closest('.mobile-fullscreen-toggle-btn') || 
            target.closest('.mobile-fullscreen-menu-btn')
        )) {
            return;
        }

        var handCard = target.closest ? target.closest('.hand-card') : null;
        var handArea = target.closest ? target.closest('.hand-area') : null;
        var badge = target.closest ? target.closest('.mobile-hand-minimized-badge') : null;

        if (!isHandExpanded) {
            if (handCard || handArea || badge) {
                e.stopPropagation();
                e.preventDefault();
                setHandState(true);
            }
            return;
        }

        if (isHandExpanded) {
            if (!handCard && !touchState.isDragging) {
                setHandState(false);
            }
        }
    }

    // 彻底禁用浏览器和 Android WebView 的默认拖拽与长按选中文本行为，杜绝 0.5s 长按延迟与系统带白边拖影
    document.addEventListener('dragstart', function(e) {
        e.preventDefault();
        return false;
    }, true);
    document.addEventListener('selectstart', function(e) {
        var tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
        if (tag !== 'input' && tag !== 'textarea') {
            e.preventDefault();
            return false;
        }
    }, true);

    // 绑定触摸事件系统
    document.addEventListener('touchstart', onTouchStart, { passive: false, capture: true });
    document.addEventListener('touchmove', onTouchMove, { passive: false, capture: true });
    document.addEventListener('touchend', onTouchEnd, { passive: false, capture: true });
    document.addEventListener('touchcancel', onTouchEnd, { passive: false, capture: true });
    document.addEventListener('click', handleInteraction, true);

    function initMobileController() {
        initButtons();
        checkBattleState();

        var observer = new MutationObserver(function() {
            checkBattleState();
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileController);
    } else {
        initMobileController();
    }
})();
