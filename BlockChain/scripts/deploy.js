const hre = require("hardhat");

async function main() {
  const CertificateSystem = await hre.ethers.getContractFactory("CertificateSystem");
  const certificateSystem = await CertificateSystem.deploy();

  await certificateSystem.deployed();

  console.log("CertificateSystem deployed to:", certificateSystem.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});