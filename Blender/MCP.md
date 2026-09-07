# Blender MCP(Claude Code / Codex 共通)  2026-09-07 設定

開いている Blender の画面に対して、Claude Code と Codex の両方からリアルタイムに操作を送るための設定。
一括生成は従来どおり headless スクリプト(`浜崎2号棟/build_house.py`)、**微調整・確認・アセット取り込みは MCP** の使い分け。

## 構成

| 要素 | 場所 | 備考 |
|---|---|---|
| Blender アドオン | `~/Library/Application Support/Blender/5.2/scripts/addons/blender_mcp_addon.py` | ahujasid/blender-mcp の addon.py(v1.6, protocol 5)。有効化済み・**テレメトリ OFF**(既定は ON なので注意) |
| MCP サーバー | `/Users/Jun/.local/bin/blender-mcp`(`uv tool install blender-mcp`, v1.9.1) | stdio。Blender の localhost:9876 に接続する |
| Claude Code | `claude mcp add blender -s user -- /Users/Jun/.local/bin/blender-mcp` 済み(user スコープ=全プロジェクト) | `claude mcp get blender` で状態確認 |
| Codex | `~/.codex/config.toml` の `[mcp_servers.blender]` | command は上と同じ。追記前のバックアップ `config.toml.bak-YYYYMMDD` |

## 使い方

1. Blender を GUI で起動する(`open -a Blender <file>.blend`)。アドオンは起動時にソケットサーバーを自動で立てる(`blendermcp_auto_start_server` 既定 True)。サイドパネル(N)→「MCP for Blender」タブで状態が見える
2. Claude Code / Codex を(Blender 起動後に)開く。MCP のツール `get_scene_info` / `get_object_info` / `execute_blender_code` / `get_viewport_screenshot` / `search_polyhaven_assets` などが使える
3. 一括で作り直すときは headless スクリプトを回し、Blender 側で File → Revert(復元)で読み直す

## 注意

- headless(`blender -b`)ではソケットサーバーは立たない(アドオンが拒否する)。MCP は GUI 起動が前提
- Blender を先に起動していないと MCP サーバーは接続エラーを返す(サーバー自体は起動する)
- アドオンを入れる前から開いていた Blender には反映されない。入れ替えたら Blender を再起動する
- `execute_blender_code` は任意の Python を Blender 内で実行する。破壊的操作(ファイル削除・保存上書き)を頼まれてもチャットで確認を取ってから

## 動作確認(2026-09-07)

- ソケット直叩き: `get_scene_info` → status success, objects 391(浜崎2号棟.blend)
- MCP 経由: `tools/list` で 28 ツール。`get_scene_info` と `execute_blender_code`(`print(len(bpy.data.objects))` → 391)が成功
- v1.9.1 のツールは全て `user_prompt` 引数が必須(テレメトリ用の文字列。空でなければ何でもよい)
