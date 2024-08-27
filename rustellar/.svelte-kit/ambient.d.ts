
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://kit.svelte.dev/docs/modules#$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://kit.svelte.dev/docs/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://kit.svelte.dev/docs/modules#$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```bash
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const TAURI_ENV_PLATFORM: string;
	export const npm_package_dependencies__tauri_apps_plugin_shell: string;
	export const TMUX: string;
	export const USER: string;
	export const npm_package_dependencies__xterm_xterm: string;
	export const npm_config_user_agent: string;
	export const STARSHIP_SHELL: string;
	export const npm_package_dependencies__tauri_apps_api: string;
	export const npm_package_devDependencies__sveltejs_vite_plugin_svelte: string;
	export const npm_package_devDependencies_vite: string;
	export const npm_node_execpath: string;
	export const BROWSER: string;
	export const SHLVL: string;
	export const HOME: string;
	export const OLDPWD: string;
	export const CAML_LD_LIBRARY_PATH: string;
	export const NVM_BIN: string;
	export const TERM_PROGRAM_VERSION: string;
	export const NVM_INC: string;
	export const OCAML_TOPLEVEL_PATH: string;
	export const npm_package_devDependencies__sveltejs_adapter_static: string;
	export const npm_package_devDependencies_svelte_check: string;
	export const npm_package_scripts_check: string;
	export const npm_package_scripts_tauri: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const TAURI_ENV_TARGET_TRIPLE: string;
	export const WSL_DISTRO_NAME: string;
	export const npm_package_description: string;
	export const npm_package_devDependencies_typescript: string;
	export const NVM_DIR: string;
	export const WAYLAND_DISPLAY: string;
	export const npm_package_scripts_dev: string;
	export const LOGNAME: string;
	export const npm_package_type: string;
	export const npm_package_devDependencies__tauri_apps_cli: string;
	export const NAME: string;
	export const PULSE_SERVER: string;
	export const WSL_INTEROP: string;
	export const _: string;
	export const npm_package_scripts_check_watch: string;
	export const npm_package_dependencies__xterm_addon_ligatures: string;
	export const npm_config_registry: string;
	export const TERM: string;
	export const TAURI_ENV_DEBUG: string;
	export const npm_config_node_gyp: string;
	export const PATH: string;
	export const NODE: string;
	export const TAURI_ENV_PLATFORM_VERSION: string;
	export const npm_package_name: string;
	export const XDG_RUNTIME_DIR: string;
	export const npm_package_dependencies__xterm_addon_search: string;
	export const npm_config_frozen_lockfile: string;
	export const DISPLAY: string;
	export const LANG: string;
	export const MACOSX_DEPLOYMENT_TARGET: string;
	export const TAURI_ENV_ARCH: string;
	export const npm_package_dependencies__xterm_addon_clipboard: string;
	export const npm_package_dependencies__xterm_addon_image: string;
	export const TERM_PROGRAM: string;
	export const npm_lifecycle_script: string;
	export const npm_package_devDependencies__sveltejs_kit: string;
	export const NODE_PATH: string;
	export const SHELL: string;
	export const npm_package_version: string;
	export const npm_package_dependencies__xterm_addon_fit: string;
	export const npm_lifecycle_event: string;
	export const npm_package_scripts_build: string;
	export const npm_package_devDependencies_svelte: string;
	export const npm_package_devDependencies_tslib: string;
	export const OPAM_SWITCH_PREFIX: string;
	export const npm_package_license: string;
	export const TAURI_ENV_FAMILY: string;
	export const CUDA_HOME: string;
	export const PWD: string;
	export const npm_execpath: string;
	export const NVM_CD_FLAGS: string;
	export const XDG_DATA_DIRS: string;
	export const PNPM_SCRIPT_SRC_DIR: string;
	export const STARSHIP_SESSION_KEY: string;
	export const npm_command: string;
	export const IPHONEOS_DEPLOYMENT_TARGET: string;
	export const TMUX_PLUGIN_MANAGER_PATH: string;
	export const npm_package_scripts_preview: string;
	export const HOSTTYPE: string;
	export const MANPATH: string;
	export const PNPM_HOME: string;
	export const TMUX_PANE: string;
	export const WSL2_GUI_APPS_ENABLED: string;
	export const INIT_CWD: string;
	export const WSLENV: string;
	export const npm_package_dependencies__xterm_addon_unicode11: string;
	export const npm_package_dependencies__xterm_addon_web_links: string;
	export const npm_package_dependencies__xterm_addon_webgl: string;
	export const NODE_ENV: string;
}

/**
 * Similar to [`$env/static/private`](https://kit.svelte.dev/docs/modules#$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://kit.svelte.dev/docs/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://kit.svelte.dev/docs/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		TAURI_ENV_PLATFORM: string;
		npm_package_dependencies__tauri_apps_plugin_shell: string;
		TMUX: string;
		USER: string;
		npm_package_dependencies__xterm_xterm: string;
		npm_config_user_agent: string;
		STARSHIP_SHELL: string;
		npm_package_dependencies__tauri_apps_api: string;
		npm_package_devDependencies__sveltejs_vite_plugin_svelte: string;
		npm_package_devDependencies_vite: string;
		npm_node_execpath: string;
		BROWSER: string;
		SHLVL: string;
		HOME: string;
		OLDPWD: string;
		CAML_LD_LIBRARY_PATH: string;
		NVM_BIN: string;
		TERM_PROGRAM_VERSION: string;
		NVM_INC: string;
		OCAML_TOPLEVEL_PATH: string;
		npm_package_devDependencies__sveltejs_adapter_static: string;
		npm_package_devDependencies_svelte_check: string;
		npm_package_scripts_check: string;
		npm_package_scripts_tauri: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		TAURI_ENV_TARGET_TRIPLE: string;
		WSL_DISTRO_NAME: string;
		npm_package_description: string;
		npm_package_devDependencies_typescript: string;
		NVM_DIR: string;
		WAYLAND_DISPLAY: string;
		npm_package_scripts_dev: string;
		LOGNAME: string;
		npm_package_type: string;
		npm_package_devDependencies__tauri_apps_cli: string;
		NAME: string;
		PULSE_SERVER: string;
		WSL_INTEROP: string;
		_: string;
		npm_package_scripts_check_watch: string;
		npm_package_dependencies__xterm_addon_ligatures: string;
		npm_config_registry: string;
		TERM: string;
		TAURI_ENV_DEBUG: string;
		npm_config_node_gyp: string;
		PATH: string;
		NODE: string;
		TAURI_ENV_PLATFORM_VERSION: string;
		npm_package_name: string;
		XDG_RUNTIME_DIR: string;
		npm_package_dependencies__xterm_addon_search: string;
		npm_config_frozen_lockfile: string;
		DISPLAY: string;
		LANG: string;
		MACOSX_DEPLOYMENT_TARGET: string;
		TAURI_ENV_ARCH: string;
		npm_package_dependencies__xterm_addon_clipboard: string;
		npm_package_dependencies__xterm_addon_image: string;
		TERM_PROGRAM: string;
		npm_lifecycle_script: string;
		npm_package_devDependencies__sveltejs_kit: string;
		NODE_PATH: string;
		SHELL: string;
		npm_package_version: string;
		npm_package_dependencies__xterm_addon_fit: string;
		npm_lifecycle_event: string;
		npm_package_scripts_build: string;
		npm_package_devDependencies_svelte: string;
		npm_package_devDependencies_tslib: string;
		OPAM_SWITCH_PREFIX: string;
		npm_package_license: string;
		TAURI_ENV_FAMILY: string;
		CUDA_HOME: string;
		PWD: string;
		npm_execpath: string;
		NVM_CD_FLAGS: string;
		XDG_DATA_DIRS: string;
		PNPM_SCRIPT_SRC_DIR: string;
		STARSHIP_SESSION_KEY: string;
		npm_command: string;
		IPHONEOS_DEPLOYMENT_TARGET: string;
		TMUX_PLUGIN_MANAGER_PATH: string;
		npm_package_scripts_preview: string;
		HOSTTYPE: string;
		MANPATH: string;
		PNPM_HOME: string;
		TMUX_PANE: string;
		WSL2_GUI_APPS_ENABLED: string;
		INIT_CWD: string;
		WSLENV: string;
		npm_package_dependencies__xterm_addon_unicode11: string;
		npm_package_dependencies__xterm_addon_web_links: string;
		npm_package_dependencies__xterm_addon_webgl: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://kit.svelte.dev/docs/modules#$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://kit.svelte.dev/docs/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * Dynamic environment variables cannot be used during prerendering.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
