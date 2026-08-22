import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { VitePWA } from "vite-plugin-pwa"
import frappeui from "frappe-ui/vite"

import path from "path"
import fs from "fs"

export default defineConfig({
	server: {
		port: 8080,
		proxy: getProxyOptions(),
		allowedHosts: true,
	},
	plugins: [
		vue(),
		frappeui({
			source: "^$",
		}),
		customProxyPlugin(),
		VitePWA({
			registerType: "autoUpdate",
			strategies: "injectManifest",
			injectRegister: null,
			devOptions: {
				enabled: true,
			},
			manifest: {
				display: "standalone",
				name: "ARIA",
				short_name: "ARIA",
				start_url: "/hrms",
				scope: "/hrms",
				id: "/hrms",
				description: "Everyday HR & Payroll operations at your fingertips",
				theme_color: "#ffffff",
				icons: [
					{
						src: "/assets/hrms/manifest/manifest-icon-192.maskable.png",
						sizes: "192x192",
						type: "image/png",
						purpose: "any",
					},
					{
						src: "/assets/hrms/manifest/manifest-icon-192.maskable.png",
						sizes: "192x192",
						type: "image/png",
						purpose: "maskable",
					},
					{
						src: "/assets/hrms/manifest/manifest-icon-512.maskable.png",
						sizes: "512x512",
						type: "image/png",
						purpose: "any",
					},
					{
						src: "/assets/hrms/manifest/manifest-icon-512.maskable.png",
						sizes: "512x512",
						type: "image/png",
						purpose: "maskable",
					},
				],
			},
		}),
	],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
		},
	},
	build: {
		outDir: "../hrms/public/frontend",
		emptyOutDir: true,
		target: "es2015",
		commonjsOptions: {
			include: [/tailwind.config.js/, /node_modules/],
		},
		sourcemap: true,
		rollupOptions: {
			output: {
				manualChunks: {
					"frappe-ui": ["frappe-ui"],
				},
			},
		},
	},
	optimizeDeps: {
		include: [
			"frappe-ui > feather-icons",
			"showdown",
			"tailwind.config.js",
			"engine.io-client",
		],
	},
})

function customProxyPlugin() {
	return {
		name: "custom-frappe-proxy",
		enforce: "post",
		config: () => ({
			server: {
				proxy: getProxyOptions(),
			},
		}),
	}
}

function getProxyOptions() {
	const config = getCommonSiteConfig()
	const webserver_port = process.env.BACKEND_PORT || (config ? config.webserver_port : 8000)
	const backend_host = process.env.BACKEND_HOST || "127.0.0.1"
	const target_site = process.env.FRAPPE_SITE || "hrms.localhost"

	if (!config) {
		console.log(`No common_site_config.json found, using backend ${backend_host}:${webserver_port}`)
	}
	return {
		"^/(app|login|api|assets|files|private)": {
			target: `http://${backend_host}:${webserver_port}`,
			ws: true,
			changeOrigin: false,
			configure: (proxy) => {
				proxy.on("proxyReq", (proxyReq, req) => {
					const hostHeader = req.headers.host || ""
					const site_name = hostHeader.split(":")[0]
					if (site_name === "localhost" || site_name === "127.0.0.1" || !site_name) {
						proxyReq.setHeader("Host", target_site)
					}
				})
			},
			router: function (req) {
				const reqHost = req.headers.host ? req.headers.host.split(":")[0] : ""
				if (reqHost && reqHost !== "localhost" && reqHost !== "127.0.0.1" && !process.env.BACKEND_HOST) {
					return `http://${reqHost}:${webserver_port}`
				}
				return `http://${backend_host}:${webserver_port}`
			},
		},
	}
}

function getCommonSiteConfig() {
	let currentDir = path.resolve(".")
	// traverse up till we find frappe-bench with sites directory
	let parentDir = path.resolve(currentDir, "..")
	while (currentDir !== parentDir) {
		if (
			fs.existsSync(path.join(currentDir, "sites")) &&
			fs.existsSync(path.join(currentDir, "apps"))
		) {
			let configPath = path.join(currentDir, "sites", "common_site_config.json")
			if (fs.existsSync(configPath)) {
				return JSON.parse(fs.readFileSync(configPath))
			}
			return null
		}
		currentDir = parentDir
		parentDir = path.resolve(currentDir, "..")
	}
	return null
}
